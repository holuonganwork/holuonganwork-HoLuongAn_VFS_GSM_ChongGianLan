import hashlib
import json
import random
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

from sqlalchemy import insert, select, text
from sqlalchemy.orm import Session

from app.db.base import Base
from app.fraud.geo import haversine_km
from app.models.entities import Device, Driver, DriverDevice, GPSEvent, Promotion, Trip

BASE_TIME = datetime(2026, 1, 5, 0, 0, tzinfo=UTC)
TABLE_MODELS = (Driver, Promotion, Device, DriverDevice, Trip, GPSEvent)


def json_default(value: Any) -> str:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    raise TypeError(f"Cannot serialize {type(value)}")


@dataclass(frozen=True)
class SyntheticDataset:
    seed: int
    tables: dict[str, list[dict[str, Any]]]
    ground_truth: dict[str, dict[str, Any]]

    def to_json(self) -> str:
        return json.dumps(
            {
                "generator_version": "1",
                "seed": self.seed,
                "tables": self.tables,
                "ground_truth": self.ground_truth,
            },
            default=json_default,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )

    def digest(self) -> str:
        return hashlib.sha256(self.to_json().encode()).hexdigest()

    def export(self, directory: Path) -> dict[str, Any]:
        directory.mkdir(parents=True, exist_ok=True)
        payload = self.to_json()
        manifest = {
            "generator_version": "1",
            "seed": self.seed,
            "sha256": hashlib.sha256(payload.encode()).hexdigest(),
            "counts": {name: len(rows) for name, rows in self.tables.items()},
            "ground_truth": self.ground_truth,
        }
        (directory / "dataset.json").write_text(payload, encoding="utf-8")
        (directory / "manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
        )
        return manifest


def generate_dataset(
    seed: int = 42, drivers: int = 100, trips_per_driver: int = 50
) -> SyntheticDataset:
    if drivers < 50 or trips_per_driver < 12:
        raise ValueError("Injected scenarios require at least 50 drivers and 12 trips per driver")
    rng = random.Random(seed)
    days = (trips_per_driver + 9) // 10
    end_time = BASE_TIME + timedelta(days=days + 1)
    tables: dict[str, list[dict[str, Any]]] = {model.__tablename__: [] for model in TABLE_MODELS}
    tables["promotions"].append(
        {
            "id": 1,
            "code": "SYNTHETIC_TEN_TRIPS",
            "starts_at": BASE_TIME,
            "ends_at": end_time,
            "trip_threshold": 10,
            "reward_amount": Decimal("30000.00"),
            "created_at": BASE_TIME,
        }
    )
    ground_truth: dict[str, dict[str, Any]] = {}
    for driver_id in range(1, drivers + 1):
        external_id = f"D{driver_id:03}"
        tables["drivers"].append(
            {
                "id": driver_id,
                "external_driver_id": external_id,
                "name": f"Synthetic Driver {driver_id:03}",
                "status": "active",
                "created_at": BASE_TIME,
                "updated_at": BASE_TIME,
            }
        )
        tables["devices"].append(
            {
                "id": driver_id,
                "device_identifier": f"SYN-DEVICE-{driver_id:03}",
                "created_at": BASE_TIME,
            }
        )
        tables["driver_devices"].append(
            {
                "driver_id": driver_id,
                "device_id": driver_id,
                "first_seen_at": BASE_TIME,
                "last_seen_at": end_time,
            }
        )
        suspicious_ids = []
        for trip_index in range(trips_per_driver):
            trip_id = (driver_id - 1) * trips_per_driver + trip_index + 1
            start = BASE_TIME + timedelta(
                days=trip_index // 10, minutes=60 + (trip_index % 10) * 45
            )
            lat = round(10.76 + rng.uniform(-0.055, 0.055), 6)
            lng = round(106.68 + rng.uniform(-0.055, 0.055), 6)
            drop_lat = round(lat + rng.choice([-1, 1]) * rng.uniform(0.012, 0.04), 6)
            drop_lng = round(lng + rng.uniform(-0.03, 0.03), 6)
            distance = round(haversine_km(lat, lng, drop_lat, drop_lng) * 1.15, 3)
            duration = max(480, int(distance / rng.uniform(20, 35) * 3600))
            promoted = trip_index % 17 == 0
            if driver_id in (14, 50) and trip_index < 12:
                start = BASE_TIME + timedelta(minutes=60 + trip_index * 4)
                lat, lng, drop_lat, drop_lng = 10.77, 106.69, 10.772, 106.692
                distance, duration = 0.35, 120
                promoted = driver_id == 50
                suspicious_ids.append(trip_id)
            trip_end = start + timedelta(seconds=duration)
            tables["trips"].append(
                {
                    "id": trip_id,
                    "driver_id": driver_id,
                    "pickup_lat": lat,
                    "pickup_lng": lng,
                    "dropoff_lat": drop_lat,
                    "dropoff_lng": drop_lng,
                    "started_at": start,
                    "ended_at": trip_end,
                    "distance_km": distance,
                    "fare_amount": Decimal(str(round(12000 + distance * 9000, 2))),
                    "promotion_amount": Decimal("8000.00") if promoted else Decimal("0.00"),
                    "promotion_id": 1 if promoted else None,
                    "created_at": trip_end,
                }
            )
            for point in range(6):
                event_id = (trip_id - 1) * 6 + point + 1
                fraction = point / 5
                event = {
                    "id": event_id,
                    "driver_id": driver_id,
                    "trip_id": trip_id,
                    "latitude": round(lat + (drop_lat - lat) * fraction, 6),
                    "longitude": round(lng + (drop_lng - lng) * fraction, 6),
                    "recorded_at": start + timedelta(seconds=duration * fraction),
                }
                if driver_id == 1 and trip_index == 0 and point == 2:
                    event["latitude"] += 1.0
                tables["gps_events"].append(event)
        if suspicious_ids:
            ground_truth[external_id] = {
                "fraud_types": (
                    ["repeated_trips", "promotion_abuse"] if driver_id == 50 else ["repeated_trips"]
                ),
                "trip_ids": suspicious_ids,
                "scenario": "12 identical short rides in 44 minutes"
                + (" with incentive usage" if driver_id == 50 else ""),
            }
    ground_truth["D001"] = {
        "fraud_types": ["gps_spoofing"],
        "trip_ids": [1],
        "gps_event_ids": [2, 3, 4],
        "scenario": "GPS point teleports ~111 km",
    }
    shared_device_id = drivers + 1
    tables["devices"].append(
        {"id": shared_device_id, "device_identifier": "SYN-SHARED-027", "created_at": BASE_TIME}
    )
    for driver_id in (27, 28, 29):
        tables["driver_devices"].append(
            {
                "driver_id": driver_id,
                "device_id": shared_device_id,
                "first_seen_at": BASE_TIME,
                "last_seen_at": end_time,
            }
        )
        ground_truth[f"D{driver_id:03}"] = {
            "fraud_types": ["shared_device"],
            "device_ids": [shared_device_id],
            "related_driver_ids": [item for item in (27, 28, 29) if item != driver_id],
            "scenario": "Three accounts observed on one shared device",
        }
    return SyntheticDataset(seed, tables, ground_truth)


def load_dataset(session: Session, dataset: SyntheticDataset) -> None:
    """Load into an empty migrated database, atomically; never erase existing work."""
    for table in Base.metadata.sorted_tables:
        if session.execute(select(table).limit(1)).first() is not None:
            raise ValueError(
                "Synthetic import requires an empty database; existing data was preserved"
            )
    for model in TABLE_MODELS:
        rows = dataset.tables[model.__tablename__]
        for start in range(0, len(rows), 1000):
            session.execute(insert(model.__table__), rows[start : start + 1000])
    if session.get_bind().dialect.name == "postgresql":
        # Explicit deterministic IDs must not leave the next sequence value at 1.
        for model in TABLE_MODELS:
            if model is DriverDevice:
                continue
            table_name = model.__tablename__  # fixed model names, never user input
            session.execute(
                text(
                    f"SELECT setval(pg_get_serial_sequence('{table_name}', 'id'), "
                    f"(SELECT MAX(id) FROM {table_name}), true)"
                )
            )
    session.flush()
