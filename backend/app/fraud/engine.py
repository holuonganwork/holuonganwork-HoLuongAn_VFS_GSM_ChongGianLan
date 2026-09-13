"""Synchronous orchestration for the transitional modular monolith."""

import logging
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.config import DecisionPolicyConfig, RuleConfig
from app.core.enums import DecisionOutcome
from app.fraud.correlation import correlate_signals
from app.fraud.providers import Detector, RiskAssessor, RuleDetectorAdapter, RuleRiskAssessor
from app.fraud.types import DriverObservation, Signal
from app.models.entities import FraudCase
from app.processing.observations import load_observations
from app.services.detection import process_alert

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DetectionSummary:
    drivers_checked: int = 0
    cases_created: int = 0
    cases_existing: int = 0
    evidence_created: int = 0
    alerts_created: int = 0
    alerts_existing: int = 0
    auto_cleared: int = 0
    auto_fraud: int = 0
    human_review: int = 0


def detect_driver(observation: DriverObservation, config: RuleConfig) -> list[Signal]:
    return RuleDetectorAdapter().detect(observation, config)


def persist_case(
    session: Session, driver_id: int, signals: list[Signal], config: RuleConfig
) -> tuple[FraudCase | None, bool]:
    """Compatibility entry point for one incident, routed through alert and policy.

    Batch callers use run_detection, which supports several incidents per driver.
    """
    candidates = correlate_signals(driver_id, signals)
    if not candidates:
        return None, False
    if len(candidates) != 1:
        raise ValueError("Signals span multiple incidents; use run_detection")
    candidate = candidates[0]
    record = process_alert(
        session,
        candidate,
        RuleRiskAssessor().assess(candidate, config),
        config,
        DecisionPolicyConfig(),
    )
    return record.case, record.created


def run_detection(
    session: Session,
    config: RuleConfig | None = None,
    policy: DecisionPolicyConfig | None = None,
    *,
    detector: Detector | None = None,
    assessor: RiskAssessor | None = None,
) -> DetectionSummary:
    """Caller owns the transaction; model/ensemble adapters can replace either provider."""
    config = config or RuleConfig()
    policy = policy or DecisionPolicyConfig()
    detector = detector or RuleDetectorAdapter()
    assessor = assessor or RuleRiskAssessor()
    counts = dict.fromkeys(DetectionSummary.__dataclass_fields__, 0)
    for observation in load_observations(session):
        counts["drivers_checked"] += 1
        signals = detector.detect(observation, config)
        for candidate in correlate_signals(observation.driver.id, signals):
            assessment = assessor.assess(candidate, config)
            record = process_alert(session, candidate, assessment, config, policy)
            counts["alerts_created" if record.created else "alerts_existing"] += 1
            # Outcome counters count newly recorded decisions, not retry observations.
            if record.created:
                outcome_key = {
                    DecisionOutcome.AUTO_CLEAR: "auto_cleared",
                    DecisionOutcome.AUTO_FRAUD: "auto_fraud",
                    DecisionOutcome.HUMAN_REVIEW: "human_review",
                }[record.alert.decision_result.outcome]
                counts[outcome_key] += 1
            if record.case is not None:
                counts["cases_created" if record.created else "cases_existing"] += 1
                if record.created:
                    counts["evidence_created"] += len(candidate.signals)
    summary = DetectionSummary(**counts)
    logger.info("Detection batch finished: %s", summary)
    return summary
