"""Real PostgreSQL checks use isolated schemas in a dedicated test database."""

import os
import uuid
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from app.core.config import RuleConfig
from app.core.enums import CaseStatus
from app.db.base import Base
from app.db.session import get_session
from app.fraud.engine import detect_driver, persist_case, run_detection
from app.fraud.types import DriverObservation, Signal
from app.main import app
from app.models.entities import Driver, FraudCase, GPSEvent, Trip
from app.services.cases import InvalidTransitionError, decide_case, start_review
from app.services.synthetic import generate_dataset, load_dataset
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine, inspect, select, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Session

pytestmark = pytest.mark.postgres
BACKEND = Path(__file__).resolve().parents[1]


@pytest.fixture
def postgres_engine() -> Iterator[Engine]:
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set TEST_DATABASE_URL to a dedicated PostgreSQL test database")
    schema = "test_fraud_" + uuid.uuid4().hex
    admin = create_engine(url)
    if admin.dialect.name != "postgresql":
        pytest.fail("TEST_DATABASE_URL must use PostgreSQL")
    with admin.begin() as connection:
        connection.execute(text(f'CREATE SCHEMA "{schema}"'))
    engine = create_engine(url, connect_args={"options": f"-csearch_path={schema}"})
    try:
        config = Config(str(BACKEND / "alembic.ini"))
        with engine.begin() as connection:
            config.attributes["connection"] = connection
            command.upgrade(config, "head")
        yield engine
    finally:
        engine.dispose()
        with admin.begin() as connection:
            connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        admin.dispose()


def test_postgres_migration_jsonb_indexes_and_rollback(postgres_engine: Engine) -> None:
    with postgres_engine.begin() as connection:
        assert compare_metadata(MigrationContext.configure(connection), Base.metadata) == []
        columns = {col["name"]: col for col in inspect(connection).get_columns("fraud_evidences")}
        assert isinstance(columns["evidence_data"]["type"], JSONB)
        indexes = inspect(connection).get_indexes("gps_events")
        assert any(item["name"] == "ix_gps_events_trip_recorded" for item in indexes)
        config = Config(str(BACKEND / "alembic.ini"))
        config.attributes["connection"] = connection
        command.downgrade(config, "base")
        assert inspect(connection).get_table_names() == ["alembic_version"]
        command.upgrade(config, "head")


def test_postgres_complete_milestone_flow(postgres_engine: Engine) -> None:
    dataset = generate_dataset()
    with Session(postgres_engine) as session, session.begin():
        load_dataset(session, dataset)
        summary = run_detection(session)
        assert summary.cases_created == 6
        cases = {
            driver.external_driver_id: case
            for case, driver in session.execute(select(FraudCase, Driver).join(Driver))
        }
        assert {driver: set(case.fraud_types) for driver, case in cases.items()} == {
            driver: set(truth["fraud_types"]) for driver, truth in dataset.ground_truth.items()
        }
        gps_case_id = cases["D001"].id
        # Explicit seeded primary keys must leave database sequences usable.
        next_driver = Driver(external_driver_id="AFTER_SEED", name="Sequence check")
        session.add(next_driver)
        session.flush()
        assert next_driver.id == 101

    def db_override() -> Iterator[Session]:
        with Session(postgres_engine, expire_on_commit=False) as session, session.begin():
            yield session

    app.dependency_overrides[get_session] = db_override
    try:
        with TestClient(app) as client:
            response = client.get(f"/fraud-cases/{gps_case_id}")
            assert response.status_code == 200
            case = response.json()
            evidence_id = case["evidence"][0]["id"]
            sources = client.get(
                f"/fraud-cases/{gps_case_id}/evidence/{evidence_id}/sources"
            ).json()
            assert {item["source_type"] for item in sources} == {"trip", "gps_event"}
            actor = {"reviewer": "control_user_01", "reason": "Inspecting original GPS records"}
            assert client.post(f"/fraud-cases/{gps_case_id}/review", json=actor).status_code == 200
            assert (
                client.post(
                    f"/fraud-cases/{gps_case_id}/request-explanation", json=actor
                ).status_code
                == 200
            )
            assert (
                client.post(
                    f"/fraud-cases/{gps_case_id}/explanation",
                    json={"explanation": "GPS became unstable in a tunnel"},
                ).status_code
                == 201
            )
            assert (
                client.post(
                    f"/fraud-cases/{gps_case_id}/decision", json={"decision": "dismissed", **actor}
                ).status_code
                == 201
            )
    finally:
        app.dependency_overrides.clear()
    with Session(postgres_engine) as session, session.begin():
        rerun = run_detection(session)
        assert rerun.cases_created == 0
        assert rerun.cases_existing == 6
        assert session.get(FraudCase, gps_case_id).status == CaseStatus.DISMISSED
        assert session.get(Driver, 1).status == "active"


def test_concurrent_detection_and_final_decisions(postgres_engine: Engine) -> None:
    with Session(postgres_engine) as session, session.begin():
        load_dataset(session, generate_dataset(drivers=50, trips_per_driver=12))
        driver = session.get(Driver, 1)
        trips = list(session.scalars(select(Trip).where(Trip.driver_id == 1)))
        gps = list(session.scalars(select(GPSEvent).where(GPSEvent.driver_id == 1)))
        signals = detect_driver(
            DriverObservation(driver, trips, gps, [], [], {1: driver}, {}), RuleConfig()
        )

    def detect_once(signals: list[Signal]) -> bool:
        with Session(postgres_engine) as session, session.begin():
            _, created = persist_case(session, 1, signals, RuleConfig())
            return created

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(detect_once, [signals, signals]))
    assert sorted(results) == [False, True]
    with Session(postgres_engine) as session, session.begin():
        case = session.scalar(select(FraudCase))
        case_id = case.id
        start_review(session, case_id, "reviewer", "Review started")

    def decide_once(decision: CaseStatus) -> bool:
        try:
            with Session(postgres_engine) as session, session.begin():
                decide_case(session, case_id, decision, "reviewer", "Evidence reviewed")
            return True
        except InvalidTransitionError:
            return False

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(decide_once, [CaseStatus.DISMISSED, CaseStatus.CONFIRMED_FRAUD]))
    assert sorted(results) == [False, True]
