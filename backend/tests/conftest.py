from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from app.core.enums import FraudType, Severity, SourceType
from app.db.base import Base
from app.db.session import get_session
from app.fraud.types import DriverObservation, Signal, source
from app.main import app
from app.models.entities import Driver, GPSEvent, Trip
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

TIME = datetime(2026, 1, 5, tzinfo=UTC)


def make_trip(identifier: int = 1, **overrides: object) -> Trip:
    data = dict(
        id=identifier,
        driver_id=1,
        pickup_lat=10.77,
        pickup_lng=106.69,
        dropoff_lat=10.772,
        dropoff_lng=106.692,
        started_at=TIME + timedelta(minutes=4 * (identifier - 1)),
        ended_at=TIME + timedelta(minutes=4 * (identifier - 1) + 2),
        distance_km=0.35,
        fare_amount=Decimal("15000.00"),
        promotion_amount=Decimal("0.00"),
        promotion_id=None,
        created_at=TIME,
    )
    return Trip(**(data | overrides))


def observe(
    trips: list[Trip] | None = None, gps_events: list[GPSEvent] | None = None
) -> DriverObservation:
    driver = Driver(id=1, external_driver_id="D001", name="Test driver", status="active")
    return DriverObservation(driver, trips or [], gps_events or [], [], [], {1: driver}, {})


@pytest.fixture
def signal() -> Signal:
    return Signal(
        signal="impossible_speed",
        fraud_type=FraudType.GPS_SPOOFING,
        severity=Severity.HIGH,
        description="Example impossible movement",
        source_type=SourceType.TRIP,
        source_id=1,
        details={"speed_kmh": 999, "distance_km": 16.65, "elapsed_seconds": 60},
        sources=[source(SourceType.TRIP, 1)],
    )


@pytest.fixture
def engine() -> Iterator[Engine]:
    database = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )

    @event.listens_for(database, "connect")
    def foreign_keys(connection: object, record: object) -> None:
        connection.execute("PRAGMA foreign_keys=ON")

    # Lightweight tests only. The application always uses Alembic migrations.
    Base.metadata.create_all(database)
    yield database
    database.dispose()


@pytest.fixture
def session(engine: Engine) -> Iterator[Session]:
    with Session(engine, expire_on_commit=False) as db:
        db.add(Driver(id=1, external_driver_id="D001", name="Test driver", status="active"))
        db.flush()
        db.add(make_trip())
        db.commit()
        yield db


@pytest.fixture
def client(engine: Engine, session: Session) -> Iterator[TestClient]:
    def override_session() -> Iterator[Session]:
        with Session(engine, expire_on_commit=False) as db, db.begin():
            yield db

    app.dependency_overrides[get_session] = override_session
    try:
        with TestClient(app) as api_client:
            yield api_client
    finally:
        app.dependency_overrides.clear()
