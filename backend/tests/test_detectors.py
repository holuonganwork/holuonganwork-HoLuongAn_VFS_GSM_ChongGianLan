from dataclasses import replace
from datetime import timedelta
from decimal import Decimal

import pytest
from app.core.config import RuleConfig
from app.core.enums import FraudType
from app.fraud import device_detector, gps_detector, promotion_detector, repeated_trip_detector
from app.fraud.geo import haversine_km
from app.fraud.scoring import score_signals
from app.fraud.types import Signal
from app.models.entities import Device, Driver, DriverDevice, GPSEvent, Promotion
from conftest import TIME, make_trip, observe


@pytest.mark.parametrize(
    ("seconds", "latitude", "expected"),
    [
        (60, 11.77, "gps_location_jump"),
        (600, 11.77, "impossible_speed"),
        (0, 10.78, "inconsistent_gps_sequence"),
        (-10, 10.77, "inconsistent_gps_sequence"),
    ],
)
def test_gps_anomalies(seconds: int, latitude: float, expected: str) -> None:
    events = [
        GPSEvent(id=1, trip_id=1, driver_id=1, latitude=10.77, longitude=106.69, recorded_at=TIME),
        GPSEvent(
            id=2,
            trip_id=1,
            driver_id=1,
            latitude=latitude,
            longitude=106.69,
            recorded_at=TIME + timedelta(seconds=seconds),
        ),
    ]
    signal = gps_detector.detect(observe(gps_events=events), RuleConfig())[0]
    assert signal.signal == expected
    assert signal.details["elapsed_seconds"] == seconds
    assert signal.details["distance_km"] == pytest.approx(
        haversine_km(10.77, 106.69, latitude, 106.69), abs=1e-6
    )
    assert {ref.source_id for ref in signal.sources if ref.source_type == "gps_event"} == {1, 2}
    if seconds <= 0:
        assert signal.details["speed_kmh"] is None


@pytest.mark.parametrize(
    ("seconds", "latitude", "trip_id"),
    [
        (60, 10.771, 1),
        (0, 10.77, 1),
        (1, 10.770001, 1),
        (1, 20.77, 2),
    ],
)
def test_gps_normal_jitter_duplicates_and_trip_boundaries(
    seconds: int, latitude: float, trip_id: int
) -> None:
    events = [
        GPSEvent(id=1, trip_id=1, driver_id=1, latitude=10.77, longitude=106.69, recorded_at=TIME),
        GPSEvent(
            id=2,
            trip_id=trip_id,
            driver_id=1,
            latitude=latitude,
            longitude=106.69,
            recorded_at=TIME + timedelta(seconds=seconds),
        ),
    ]
    assert gps_detector.detect(observe(gps_events=events), RuleConfig()) == []


def test_repeated_routes_use_geographic_distance_and_rolling_window() -> None:
    # Straddle midnight and decimal rounding boundaries; all locations remain nearby.
    trips = [
        make_trip(
            i + 1,
            pickup_lat=10.76999 + i * 0.00002,
            started_at=TIME + timedelta(hours=23, minutes=4 * i),
            ended_at=TIME + timedelta(hours=23, minutes=4 * i + 2),
        )
        for i in range(12)
    ]
    signals = repeated_trip_detector.detect(observe(trips), RuleConfig())
    assert len(signals) == 1
    assert signals[0].details["trip_count"] == 12
    assert len(signals[0].sources) == 12


@pytest.mark.parametrize("kind", ["few", "long", "different_dropoffs", "spread_days"])
def test_repeated_trip_negatives(kind: str) -> None:
    trips = [make_trip(i + 1) for i in range(7 if kind == "few" else 10)]
    for i, trip in enumerate(trips):
        if kind == "long":
            trip.distance_km = 5
        if kind == "different_dropoffs":
            trip.dropoff_lat += i * 0.02
        if kind == "spread_days":
            trip.started_at += timedelta(days=i)
            trip.ended_at += timedelta(days=i)
    assert repeated_trip_detector.detect(observe(trips), RuleConfig()) == []


def test_shared_device_links_distinct_accounts_and_observation_times() -> None:
    drivers = {i: Driver(id=i, external_driver_id=f"D{i:03}", name="Test") for i in (1, 2, 3)}
    memberships = [
        DriverDevice(driver_id=i, device_id=10, first_seen_at=TIME, last_seen_at=TIME)
        for i in drivers
    ]
    observation = replace(
        observe(),
        devices=[Device(id=10, device_identifier="shared")],
        device_memberships=memberships,
        related_drivers=drivers,
    )
    signal = device_detector.detect(observation, RuleConfig())[0]
    assert signal.details["related_external_driver_ids"] == ["D002", "D003"]
    assert len(signal.sources) == 4
    assert (
        device_detector.detect(
            replace(observation, device_memberships=memberships[:2]), RuleConfig()
        )
        == []
    )


def test_promotion_evidence_has_denominator_threshold_and_original_trips() -> None:
    trips = [make_trip(i + 1, promotion_id=1, promotion_amount=Decimal("8000")) for i in range(12)]
    promotion = Promotion(
        id=1,
        code="TEST",
        starts_at=TIME,
        ends_at=TIME + timedelta(days=2),
        trip_threshold=10,
        reward_amount=Decimal("30000"),
    )
    observation = replace(observe(trips), promotions={1: promotion})
    signal = promotion_detector.detect(observation, RuleConfig())[0]
    assert signal.details["total_trip_count"] == 12
    assert signal.details["promotion_ratio"] == 1
    assert signal.details["short_ratio"] == 1
    assert signal.details["promotion_amount_total"] == "96000"
    assert len(signal.sources) == 13


@pytest.mark.parametrize(
    "kind",
    [
        "few",
        "normal_length",
        "outside_period",
        "not_rewarded",
        "below_threshold",
        "low_ratio",
        "zero_duration",
    ],
)
def test_promotion_negatives(kind: str) -> None:
    trips = [
        make_trip(i + 1, promotion_id=1, promotion_amount=Decimal("8000"))
        for i in range(5 if kind == "few" else 12)
    ]
    promotion = Promotion(
        id=1,
        code="TEST",
        starts_at=TIME,
        ends_at=TIME + timedelta(days=2),
        trip_threshold=10,
        reward_amount=Decimal("30000"),
    )
    for trip in trips:
        if kind == "normal_length":
            trip.distance_km = 5
        if kind == "not_rewarded":
            trip.promotion_amount = Decimal("0")
        if kind == "zero_duration":
            trip.ended_at = trip.started_at
    if kind == "outside_period":
        promotion.ends_at = TIME - timedelta(days=1)
    if kind == "below_threshold":
        promotion.trip_threshold = 20
    if kind == "low_ratio":
        trips.extend(
            make_trip(
                i + 100,
                started_at=TIME + timedelta(minutes=i * 4),
                ended_at=TIME + timedelta(minutes=i * 4 + 2),
            )
            for i in range(20)
        )
    assert (
        promotion_detector.detect(replace(observe(trips), promotions={1: promotion}), RuleConfig())
        == []
    )


def test_scoring_counts_categories_once_and_caps_at_100(signal: Signal) -> None:
    signals = [signal] * 20 + [
        signal.model_copy(update={"fraud_type": category}) for category in FraudType
    ]
    score = score_signals(signals, RuleConfig())
    assert score.total == 100
    assert score.contributions["gps_spoofing"] == 30
    assert sum(score.contributions.values()) == 100
    assert score.primary_category == FraudType.GPS_SPOOFING
    heavy = RuleConfig(weights={category: 50 for category in FraudType})
    assert score_signals(signals, heavy).total == 100
    assert sum(score_signals(signals, heavy).contributions.values()) == 200
    assert score_signals([], RuleConfig()).total == 0
    assert score_signals([], RuleConfig()).primary_category is None


def test_settings_reject_incomplete_weights_and_invalid_thresholds() -> None:
    with pytest.raises(ValueError):
        RuleConfig(weights={FraudType.GPS_SPOOFING: 30})
    with pytest.raises(ValueError):
        RuleConfig(gps_max_speed_kmh=0)
    with pytest.raises(ValueError):
        RuleConfig(gps_max_speed_kmh=float("inf"))
    with pytest.raises(ValueError):
        RuleConfig(weights={category: -1 for category in FraudType})
    for weight in (True, 30.5, "30"):
        with pytest.raises(ValueError):
            RuleConfig(weights={category: weight for category in FraudType})
