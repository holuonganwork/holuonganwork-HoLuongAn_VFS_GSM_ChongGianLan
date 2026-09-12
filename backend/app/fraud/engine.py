import hashlib
import json
import logging
from collections import defaultdict
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import RuleConfig
from app.core.enums import CaseStatus
from app.fraud import device_detector, gps_detector, promotion_detector, repeated_trip_detector
from app.fraud.scoring import score_signals
from app.fraud.types import DriverObservation, Signal
from app.models.entities import (
    Device,
    Driver,
    DriverDevice,
    EvidenceSource,
    FraudCase,
    FraudEvidence,
    GPSEvent,
    Promotion,
    Trip,
)

logger = logging.getLogger(__name__)
DETECTORS = (
    gps_detector.detect,
    repeated_trip_detector.detect,
    device_detector.detect,
    promotion_detector.detect,
)


@dataclass(frozen=True)
class DetectionSummary:
    drivers_checked: int
    cases_created: int
    cases_existing: int
    evidence_created: int


def detect_driver(observation: DriverObservation, config: RuleConfig) -> list[Signal]:
    return [signal for detector in DETECTORS for signal in detector(observation, config)]


def persist_case(
    session: Session, driver_id: int, signals: list[Signal], config: RuleConfig
) -> tuple[FraudCase | None, bool]:
    if not signals:
        return None, False
    # Serialize detection for this driver. PostgreSQL releases the lock at transaction end.
    driver = session.scalar(select(Driver).where(Driver.id == driver_id).with_for_update())
    if driver is None:
        raise ValueError(f"Unknown driver {driver_id}")
    canonical_signals = sorted(
        [signal.model_dump(mode="json") for signal in signals],
        key=lambda value: json.dumps(value, sort_keys=True),
    )
    fingerprint = hashlib.sha256(
        json.dumps(
            {
                "driver_id": driver_id,
                "signals": canonical_signals,
                "rule_config": config.model_dump(mode="json"),
            },
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode()
    ).hexdigest()
    existing = session.scalar(
        select(FraudCase).where(FraudCase.detection_fingerprint == fingerprint)
    )
    if existing is not None:
        return existing, False
    score = score_signals(signals, config)
    assert score.primary_category is not None
    case = FraudCase(
        driver_id=driver_id,
        fraud_type=score.primary_category,
        fraud_types=sorted(score.contributions),
        risk_score=score.total,
        score_breakdown=score.contributions,
        rule_config=config.model_dump(mode="json"),
        detection_fingerprint=fingerprint,
        status=CaseStatus.DETECTED,
    )
    session.add(case)
    session.flush()
    for signal in sorted(signals, key=lambda item: (item.fraud_type, item.signal, item.source_id)):
        evidence = FraudEvidence(
            case_id=case.id,
            fraud_type=signal.fraud_type,
            evidence_type=signal.signal,
            source_type=signal.source_type,
            source_id=signal.source_id,
            severity=signal.severity,
            score=config.weights[signal.fraud_type],
            description=signal.description,
            evidence_data=signal.model_dump(mode="json")["details"],
        )
        session.add(evidence)
        session.flush()
        refs = {(ref.source_type, ref.source_id) for ref in signal.sources}
        refs.add((signal.source_type, signal.source_id))
        for source_type, source_id in sorted(refs):
            session.add(
                EvidenceSource(
                    evidence_id=evidence.id,
                    source_type=source_type,
                    source_id=source_id,
                    **{f"{source_type.value}_id": source_id},
                )
            )
    session.flush()
    return case, True


def run_detection(session: Session, config: RuleConfig | None = None) -> DetectionSummary:
    """Caller owns the transaction. A small batch fits the milestone's 5,000 trips."""
    config = config or RuleConfig()
    drivers = {driver.id: driver for driver in session.scalars(select(Driver).order_by(Driver.id))}
    trips: dict[int, list[Trip]] = defaultdict(list)
    for trip in session.scalars(select(Trip).order_by(Trip.id)):
        trips[trip.driver_id].append(trip)
    gps: dict[int, list[GPSEvent]] = defaultdict(list)
    for event in session.scalars(select(GPSEvent).order_by(GPSEvent.id)):
        gps[event.driver_id].append(event)
    devices = {device.id: device for device in session.scalars(select(Device))}
    memberships = list(session.scalars(select(DriverDevice)))
    by_device: dict[int, list[DriverDevice]] = defaultdict(list)
    by_driver: dict[int, list[int]] = defaultdict(list)
    for membership in memberships:
        by_device[membership.device_id].append(membership)
        by_driver[membership.driver_id].append(membership.device_id)
    promotions = {promo.id: promo for promo in session.scalars(select(Promotion))}
    created = existing = evidence_count = 0
    for driver in drivers.values():
        device_ids = sorted(by_driver[driver.id])
        observation = DriverObservation(
            driver=driver,
            trips=trips[driver.id],
            gps_events=gps[driver.id],
            devices=[devices[device_id] for device_id in device_ids],
            device_memberships=[item for device_id in device_ids for item in by_device[device_id]],
            related_drivers=drivers,
            promotions=promotions,
        )
        signals = detect_driver(observation, config)
        case, is_new = persist_case(session, driver.id, signals, config)
        if case is not None:
            created += int(is_new)
            existing += int(not is_new)
            evidence_count += len(signals) if is_new else 0
    summary = DetectionSummary(len(drivers), created, existing, evidence_count)
    logger.info("Detection batch finished: %s", summary)
    return summary
