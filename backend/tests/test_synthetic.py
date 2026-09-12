import pytest
from app.fraud.engine import run_detection
from app.models.entities import Driver, FraudCase, GPSEvent, Trip
from app.services.synthetic import generate_dataset, load_dataset
from sqlalchemy import Engine, func, select
from sqlalchemy.orm import Session


def test_generator_is_deterministic_and_ground_truth_is_injected() -> None:
    first = generate_dataset(seed=42, drivers=50, trips_per_driver=12)
    assert first.to_json() == generate_dataset(seed=42, drivers=50, trips_per_driver=12).to_json()
    assert first.digest() != generate_dataset(seed=43, drivers=50, trips_per_driver=12).digest()
    assert first.ground_truth["D014"]["trip_ids"] == list(range(157, 169))
    assert first.ground_truth["D050"]["fraud_types"] == ["repeated_trips", "promotion_abuse"]
    assert (
        first.tables["gps_events"][2]["latitude"] - first.tables["gps_events"][1]["latitude"] > 0.9
    )


def test_default_dataset_end_to_end(engine: Engine) -> None:
    dataset = generate_dataset()
    with Session(engine) as session, session.begin():
        load_dataset(session, dataset)
        assert session.scalar(select(func.count()).select_from(Driver)) == 100
        assert session.scalar(select(func.count()).select_from(Trip)) == 5000
        assert session.scalar(select(func.count()).select_from(GPSEvent)) == 30000
        summary = run_detection(session)
        assert summary.drivers_checked == 100
        assert summary.cases_created == 6
        results = {
            driver.external_driver_id: set(case.fraud_types)
            for case, driver in session.execute(select(FraudCase, Driver).join(Driver))
        }
        assert results == {
            driver: set(truth["fraud_types"]) for driver, truth in dataset.ground_truth.items()
        }
        second = run_detection(session)
        assert second.cases_created == 0
        assert second.cases_existing == 6


def test_import_refuses_to_overwrite_data(engine: Engine) -> None:
    dataset = generate_dataset(drivers=50, trips_per_driver=12)
    with Session(engine) as session, session.begin():
        load_dataset(session, dataset)
    with Session(engine) as session, session.begin():
        with pytest.raises(ValueError, match="empty database"):
            load_dataset(session, dataset)
        assert session.scalar(select(func.count()).select_from(Trip)) == 600


def test_generator_validates_scenario_size() -> None:
    with pytest.raises(ValueError):
        generate_dataset(drivers=49)
    with pytest.raises(ValueError):
        generate_dataset(trips_per_driver=11)
