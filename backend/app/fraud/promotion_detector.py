from datetime import timedelta

from app.core.config import RuleConfig
from app.core.enums import FraudType, Severity, SourceType
from app.fraud.repeated_trip_detector import is_short
from app.fraud.types import DriverObservation, Signal, source
from app.models.entities import Trip


def detect(observation: DriverObservation, config: RuleConfig) -> list[Signal]:
    signals = []
    for promo in sorted(observation.promotions.values(), key=lambda item: item.id):
        eligible = sorted(
            (
                trip
                for trip in observation.trips
                if promo.starts_at <= trip.started_at and trip.ended_at <= promo.ends_at
            ),
            key=lambda trip: (trip.started_at, trip.id),
        )
        best: tuple[list[Trip], list[Trip], list[Trip]] | None = None
        for index, anchor in enumerate(eligible):
            window_end = anchor.started_at + timedelta(hours=24)
            window = [trip for trip in eligible[index:] if trip.started_at < window_end]
            promoted = [
                trip
                for trip in window
                if trip.promotion_id == promo.id and trip.promotion_amount > 0
            ]
            short = [trip for trip in promoted if is_short(trip, config)]
            if (
                len(promoted) >= max(config.promotion_min_trips, promo.trip_threshold)
                and len(promoted) / len(window) >= config.promotion_min_ratio
                and len(short) / len(promoted) >= config.promotion_min_short_ratio
            ):
                if best is None or len(promoted) > len(best[1]):
                    best = window, promoted, short
        if best is None:
            continue
        window, promoted, short = best
        signals.append(
            Signal(
                signal="promotion_short_trip_burst",
                fraud_type=FraudType.PROMOTION_ABUSE,
                severity=Severity.HIGH,
                description="Many rewarded short trips meet a promotion threshold.",
                source_type=SourceType.PROMOTION,
                source_id=promo.id,
                details={
                    "promotion_code": promo.code,
                    "trip_threshold": promo.trip_threshold,
                    "reward_amount": str(promo.reward_amount),
                    "window_start": window[0].started_at.isoformat(),
                    "window_end": min(
                        window[0].started_at + timedelta(hours=24), promo.ends_at
                    ).isoformat(),
                    "total_trip_count": len(window),
                    "promoted_trip_count": len(promoted),
                    "short_promoted_trip_count": len(short),
                    "promotion_ratio": len(promoted) / len(window),
                    "short_ratio": len(short) / len(promoted),
                    "promotion_amount_total": str(sum(trip.promotion_amount for trip in promoted)),
                    "trip_ids": [trip.id for trip in window],
                    "promoted_trip_ids": [trip.id for trip in promoted],
                    "short_trip_ids": [trip.id for trip in short],
                    "min_promoted_trips": config.promotion_min_trips,
                    "min_promotion_ratio": config.promotion_min_ratio,
                    "min_short_ratio": config.promotion_min_short_ratio,
                    "max_short_distance_km": config.repeat_max_distance_km,
                    "max_short_duration_seconds": config.repeat_max_duration_seconds,
                },
                sources=[source(SourceType.PROMOTION, promo.id)]
                + [source(SourceType.TRIP, trip.id) for trip in window],
            )
        )
    return signals
