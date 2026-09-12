from collections import defaultdict

from app.core.config import RuleConfig
from app.core.enums import FraudType, Severity, SourceType
from app.fraud.geo import haversine_km
from app.fraud.types import DriverObservation, Signal, source
from app.models.entities import GPSEvent


def detect(observation: DriverObservation, config: RuleConfig) -> list[Signal]:
    tracks: dict[int, list[GPSEvent]] = defaultdict(list)
    # IDs represent ingestion sequence in milestone 1, not recorded-time order.
    for event in sorted(observation.gps_events, key=lambda item: item.id):
        tracks[event.trip_id].append(event)
    signals = []
    for trip_id, events in sorted(tracks.items()):
        for previous, current in zip(events, events[1:], strict=False):
            elapsed = (current.recorded_at - previous.recorded_at).total_seconds()
            distance = haversine_km(
                previous.latitude, previous.longitude, current.latitude, current.longitude
            )
            speed = distance / elapsed * 3600 if elapsed > 0 else None
            if elapsed < 0 or (elapsed == 0 and distance >= config.gps_min_distance_km):
                rule = "inconsistent_gps_sequence"
            elif distance < config.gps_min_distance_km:
                continue
            elif elapsed <= config.gps_jump_seconds and distance >= config.gps_jump_distance_km:
                rule = "gps_location_jump"
            elif speed is not None and speed > config.gps_max_speed_kmh:
                rule = "impossible_speed"
            else:
                continue
            signals.append(
                Signal(
                    signal=rule,
                    fraud_type=FraudType.GPS_SPOOFING,
                    severity=Severity.HIGH,
                    description="Consecutive GPS observations exceed example movement limits.",
                    source_type=SourceType.TRIP,
                    source_id=trip_id,
                    details={
                        "distance_km": round(distance, 6),
                        "elapsed_seconds": elapsed,
                        "speed_kmh": round(speed, 3) if speed is not None else None,
                        "from": {
                            "gps_event_id": previous.id,
                            "latitude": previous.latitude,
                            "longitude": previous.longitude,
                            "recorded_at": previous.recorded_at.isoformat(),
                        },
                        "to": {
                            "gps_event_id": current.id,
                            "latitude": current.latitude,
                            "longitude": current.longitude,
                            "recorded_at": current.recorded_at.isoformat(),
                        },
                        "max_speed_kmh": config.gps_max_speed_kmh,
                        "jump_distance_km": config.gps_jump_distance_km,
                        "jump_seconds": config.gps_jump_seconds,
                        "min_distance_km": config.gps_min_distance_km,
                    },
                    sources=[
                        source(SourceType.TRIP, trip_id),
                        source(SourceType.GPS_EVENT, previous.id),
                        source(SourceType.GPS_EVENT, current.id),
                    ],
                )
            )
    return signals
