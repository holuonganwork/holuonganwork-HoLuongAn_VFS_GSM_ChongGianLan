from datetime import timedelta

from app.core.config import RuleConfig
from app.core.enums import FraudType, Severity, SourceType
from app.fraud.geo import haversine_km
from app.fraud.types import DriverObservation, Signal, source
from app.models.entities import Trip


def is_short(trip: Trip, config: RuleConfig) -> bool:
    return (
        0 <= trip.distance_km <= config.repeat_max_distance_km
        and 0
        < (trip.ended_at - trip.started_at).total_seconds()
        <= config.repeat_max_duration_seconds
    )


def same_route(first: Trip, second: Trip, radius_km: float) -> bool:
    return (
        haversine_km(first.pickup_lat, first.pickup_lng, second.pickup_lat, second.pickup_lng)
        <= radius_km
        and haversine_km(
            first.dropoff_lat, first.dropoff_lng, second.dropoff_lat, second.dropoff_lng
        )
        <= radius_km
    )


def detect(observation: DriverObservation, config: RuleConfig) -> list[Signal]:
    candidates = sorted(
        (trip for trip in observation.trips if is_short(trip, config)),
        key=lambda trip: (trip.started_at, trip.id),
    )
    best: list[Trip] = []
    radius = config.repeat_radius_km
    for index, anchor in enumerate(candidates):
        window_end = anchor.started_at + timedelta(hours=config.repeat_window_hours)
        group = [
            trip
            for trip in candidates[index:]
            if trip.started_at < window_end and same_route(anchor, trip, radius)
        ]
        if len(group) > len(best):
            best = group
    if len(best) < config.repeat_min_trips:
        return []
    anchor = best[0]
    return [
        Signal(
            signal="repeated_short_route",
            fraud_type=FraudType.REPEATED_TRIPS,
            severity=Severity.HIGH,
            description="Many short trips repeat a nearby pickup/drop-off route.",
            source_type=SourceType.TRIP,
            source_id=anchor.id,
            details={
                "trip_ids": [trip.id for trip in best],
                "trip_count": len(best),
                "window_start": anchor.started_at.isoformat(),
                "window_end": (
                    anchor.started_at + timedelta(hours=config.repeat_window_hours)
                ).isoformat(),
                "radius_km": radius,
                "min_trips": config.repeat_min_trips,
                "max_distance_km": config.repeat_max_distance_km,
                "max_duration_seconds": config.repeat_max_duration_seconds,
                "anchor_pickup": [anchor.pickup_lat, anchor.pickup_lng],
                "anchor_dropoff": [anchor.dropoff_lat, anchor.dropoff_lng],
                "max_pickup_distance_km": round(
                    max(
                        haversine_km(
                            anchor.pickup_lat, anchor.pickup_lng, trip.pickup_lat, trip.pickup_lng
                        )
                        for trip in best
                    ),
                    6,
                ),
                "max_dropoff_distance_km": round(
                    max(
                        haversine_km(
                            anchor.dropoff_lat,
                            anchor.dropoff_lng,
                            trip.dropoff_lat,
                            trip.dropoff_lng,
                        )
                        for trip in best
                    ),
                    6,
                ),
                "span_seconds": (best[-1].started_at - anchor.started_at).total_seconds(),
            },
            sources=[source(SourceType.TRIP, trip.id) for trip in best],
        )
    ]
