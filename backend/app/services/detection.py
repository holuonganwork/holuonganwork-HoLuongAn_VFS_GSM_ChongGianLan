"""Transactional Alert -> Decision -> optional Case persistence, reusable by a worker."""

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import DecisionPolicyConfig, RuleConfig
from app.core.enums import CaseStatus, DecisionActor, DecisionOutcome, Severity
from app.decision.policy import evaluate
from app.fraud.contracts import AlertCandidate, Assessment
from app.fraud.correlation import canonical_signals, fingerprint
from app.fraud.scoring import score_signals
from app.models.entities import (
    CaseDecision,
    CaseStatusEvent,
    DecisionResult,
    Driver,
    EvidenceSource,
    FraudAlert,
    FraudCase,
    FraudEvidence,
)


@dataclass(frozen=True)
class DetectionRecord:
    alert: FraudAlert
    case: FraudCase | None
    created: bool


def process_alert(
    session: Session,
    candidate: AlertCandidate,
    assessment: Assessment,
    rules: RuleConfig,
    policy: DecisionPolicyConfig,
) -> DetectionRecord:
    """Caller owns commit/rollback. Retries reuse the entire immutable decision snapshot."""
    driver = session.scalar(
        select(Driver).where(Driver.id == candidate.driver_id).with_for_update()
    )
    if driver is None:
        raise ValueError(f"Unknown driver {candidate.driver_id}")
    signals = canonical_signals(candidate.signals)
    detection_id = fingerprint(
        {
            "driver_id": candidate.driver_id,
            "correlation_key": candidate.correlation_key,
            "signals": signals,
            "rule_config": rules.model_dump(mode="json"),
            "assessment": assessment.model_dump(mode="json"),
            "policy": policy.model_dump(mode="json"),
        }
    )
    existing = session.scalar(
        select(FraudAlert).where(FraudAlert.detection_fingerprint == detection_id)
    )
    if existing is not None:
        case = session.scalar(select(FraudCase).where(FraudCase.alert_id == existing.id))
        return DetectionRecord(existing, case, False)

    score = score_signals(candidate.signals, rules)
    decision = evaluate(assessment, policy)
    alert = FraudAlert(
        driver_id=candidate.driver_id,
        correlation_key=candidate.correlation_key,
        detection_fingerprint=detection_id,
        fraud_type=score.primary_category,
        fraud_types=sorted(score.contributions),
        severity=(
            Severity.HIGH
            if any(s.severity == Severity.HIGH for s in candidate.signals)
            else Severity.MEDIUM
        ),
        risk_score=assessment.risk_score,
        fraud_probability=assessment.fraud_probability,
        confidence=assessment.confidence,
        impact=assessment.impact,
        model_version=assessment.model_version,
        assessment=assessment.model_dump(mode="json"),
        rule_config=rules.model_dump(mode="json"),
        signals=signals,
    )
    alert.decision_result = DecisionResult(
        outcome=decision.outcome,
        reason=decision.reason,
        policy_version=policy.version,
        policy_config=policy.model_dump(mode="json"),
    )
    session.add(alert)
    session.flush()
    if decision.outcome == DecisionOutcome.AUTO_CLEAR:
        return DetectionRecord(alert, None, True)

    automatic = decision.outcome == DecisionOutcome.AUTO_FRAUD
    case = FraudCase(
        alert_id=alert.id,
        driver_id=candidate.driver_id,
        fraud_type=alert.fraud_type,
        fraud_types=alert.fraud_types,
        risk_score=assessment.risk_score,
        # Rule contributions remain traceable even when a future model supplies the risk score.
        score_breakdown=score.contributions,
        rule_config=alert.rule_config,
        detection_fingerprint=detection_id,
        status=CaseStatus.CONFIRMED_FRAUD if automatic else CaseStatus.DETECTED,
    )
    session.add(case)
    session.flush()
    for signal in candidate.signals:
        evidence = FraudEvidence(
            case_id=case.id,
            fraud_type=signal.fraud_type,
            evidence_type=signal.signal,
            source_type=signal.source_type,
            source_id=signal.source_id,
            severity=signal.severity,
            score=rules.weights[signal.fraud_type],
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
    if automatic:
        actor = f"decision-engine:{policy.version}"
        case.decisions.append(
            CaseDecision(
                decision=CaseStatus.CONFIRMED_FRAUD,
                reviewer=actor,
                actor_type=DecisionActor.SYSTEM,
                reason=decision.reason,
            )
        )
        case.status_events.append(
            CaseStatusEvent(
                from_status=CaseStatus.DETECTED,
                to_status=CaseStatus.CONFIRMED_FRAUD,
                actor=actor,
                reason=decision.reason,
            )
        )
    session.flush()
    return DetectionRecord(alert, case, True)
