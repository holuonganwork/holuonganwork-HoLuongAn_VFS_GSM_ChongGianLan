import pytest
from app.core.config import DecisionPolicyConfig, RuleConfig
from app.core.enums import CaseStatus, DecisionActor, DecisionOutcome, FraudType, Impact, SourceType
from app.decision.policy import evaluate
from app.fraud.contracts import Assessment
from app.fraud.correlation import correlate_signals
from app.fraud.engine import run_detection
from app.fraud.providers import RuleRiskAssessor
from app.fraud.types import Signal, source
from app.models.entities import DecisionResult, Driver, FraudAlert, FraudCase, FraudEvidence
from app.services.cases import decide_case, start_review
from app.services.detection import process_alert
from conftest import make_trip
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


def estimate(**updates: object) -> Assessment:
    return Assessment(
        **{
            "risk_score": 10,
            "fraud_probability": 0.05,
            "confidence": 0.95,
            "impact": Impact.LOW,
            "model_version": "test-model-v1",
        }
        | updates
    )


@pytest.mark.parametrize(
    ("updates", "outcome"),
    [
        ({}, DecisionOutcome.AUTO_CLEAR),
        (
            {"fraud_probability": 0.1, "confidence": 0.9, "risk_score": 20},
            DecisionOutcome.AUTO_CLEAR,
        ),
        ({"fraud_probability": 0.95}, DecisionOutcome.AUTO_FRAUD),
        ({"fraud_probability": 0.5}, DecisionOutcome.HUMAN_REVIEW),
        ({"risk_score": 21}, DecisionOutcome.HUMAN_REVIEW),
        ({"confidence": 0.89}, DecisionOutcome.HUMAN_REVIEW),
        ({"confidence": None}, DecisionOutcome.HUMAN_REVIEW),
        ({"fraud_probability": None}, DecisionOutcome.HUMAN_REVIEW),
        ({"conflicting_signals": True}, DecisionOutcome.HUMAN_REVIEW),
        ({"impact": Impact.UNKNOWN}, DecisionOutcome.HUMAN_REVIEW),
        ({"impact": Impact.HIGH, "fraud_probability": 0.99}, DecisionOutcome.HUMAN_REVIEW),
        ({"impact": Impact.CRITICAL, "fraud_probability": 0.99}, DecisionOutcome.HUMAN_REVIEW),
    ],
)
def test_policy_routes_independent_probability_confidence_and_impact(updates, outcome) -> None:
    assert evaluate(estimate(**updates), DecisionPolicyConfig()).outcome == outcome


def test_invalid_estimates_and_overlapping_policy_are_rejected() -> None:
    for patch in ({"fraud_probability": 1.1}, {"confidence": float("nan")}, {"risk_score": -1}):
        with pytest.raises(ValidationError):
            estimate(**patch)
    with pytest.raises(ValidationError):
        DecisionPolicyConfig(auto_clear_max_probability=0.95)


def test_rules_do_not_invent_probability_or_confidence(signal: Signal) -> None:
    candidate = correlate_signals(1, [signal])[0]
    result = RuleRiskAssessor().assess(candidate, RuleConfig())
    assert result.risk_score == 30
    assert result.fraud_probability is result.confidence is None
    assert result.model_version == "rules:demo-v1"
    assert evaluate(result, DecisionPolicyConfig()).outcome == DecisionOutcome.HUMAN_REVIEW
    assert candidate.signals[0].fraud_category == "location_fraud"


def test_correlation_splits_unrelated_incidents_and_merges_shared_evidence(signal: Signal) -> None:
    unrelated = signal.model_copy(
        update={
            "source_id": 2,
            "sources": [source(SourceType.TRIP, 2)],
        }
    )
    assert len(correlate_signals(1, [signal, unrelated])) == 2
    bridge = signal.model_copy(
        update={
            "fraud_type": FraudType.PROMOTION_ABUSE,
            "sources": [source(SourceType.TRIP, 1), source(SourceType.TRIP, 2)],
        }
    )
    first = correlate_signals(1, [signal, unrelated, bridge])
    again = correlate_signals(1, [bridge, unrelated, signal, signal])
    assert len(first) == len(again) == 1
    assert first[0].correlation_key == again[0].correlation_key
    assert len(again[0].signals) == 3


@pytest.mark.parametrize("kind", [SourceType.DRIVER, SourceType.DEVICE, SourceType.PROMOTION])
def test_shared_identity_alone_does_not_merge_incidents(signal: Signal, kind: SourceType) -> None:
    first = signal.model_copy(update={"source_type": kind, "sources": []})
    other = first.model_copy(update={"signal": "different_incident"})
    assert len(correlate_signals(1, [first, other])) == 2


@pytest.mark.parametrize(
    ("assessment", "outcome", "status"),
    [
        (estimate(), DecisionOutcome.AUTO_CLEAR, None),
        (estimate(fraud_probability=0.99), DecisionOutcome.AUTO_FRAUD, CaseStatus.CONFIRMED_FRAUD),
        (estimate(confidence=0.5), DecisionOutcome.HUMAN_REVIEW, CaseStatus.DETECTED),
    ],
)
def test_decision_persistence_api_and_retries(
    session: Session,
    client: TestClient,
    signal: Signal,
    assessment,
    outcome,
    status,
) -> None:
    candidate = correlate_signals(1, [signal])[0]
    record = process_alert(session, candidate, assessment, RuleConfig(), DecisionPolicyConfig())
    session.commit()
    assert record.created
    assert record.alert.decision_result.outcome == outcome
    if status is None:
        assert record.case is None
        assert session.scalar(select(func.count()).select_from(FraudEvidence)) == 0
    else:
        assert record.case.status == status
        assert record.case.alert_id == record.alert.id
        assert record.case.evidence[0].sources[0].trip_id == 1
        if outcome == DecisionOutcome.AUTO_FRAUD:
            assert record.case.decisions[0].actor_type == DecisionActor.SYSTEM
            assert len(record.case.status_events) == 1
        else:
            assert record.case.decisions == []
    assert session.get(Driver, 1).status == "active"
    detail = client.get(f"/fraud-alerts/{record.alert.id}").json()
    assert detail["decision_result"]["policy_version"] == "policy-v1"
    assert detail["signals"][0]["details"]["speed_kmh"] == 999
    assert len(client.get(f"/fraud-alerts?outcome={outcome}").json()) == 1
    queue = client.get("/review-queue").json()
    assert len(queue) == (1 if outcome == DecisionOutcome.HUMAN_REVIEW else 0)
    replay = process_alert(session, candidate, assessment, RuleConfig(), DecisionPolicyConfig())
    assert not replay.created and replay.alert.id == record.alert.id
    assert session.scalar(select(func.count()).select_from(DecisionResult)) == 1


def test_pipeline_handles_multiple_incidents_and_counts_retry_outcomes(
    session: Session,
    signal: Signal,
) -> None:
    session.add(make_trip(2))
    session.commit()
    second = signal.model_copy(
        update={
            "source_id": 2,
            "sources": [source(SourceType.TRIP, 2)],
        }
    )

    class TwoIncidents:
        def detect(self, observation, config):
            return [signal, second]

    class TestAssessor:
        def assess(self, candidate, config):
            return estimate(fraud_probability=0.99 if candidate.signals[0].source_id == 2 else 0.05)

    summary = run_detection(session, detector=TwoIncidents(), assessor=TestAssessor())
    assert summary.alerts_created == 2
    assert summary.auto_cleared == summary.auto_fraud == summary.cases_created == 1
    assert summary.human_review == 0
    replay = run_detection(session, detector=TwoIncidents(), assessor=TestAssessor())
    assert replay.alerts_existing == 2 and replay.cases_existing == 1
    assert replay.auto_cleared == replay.auto_fraud == replay.cases_created == 0


def test_failed_evidence_rolls_back_alert_decision_and_case(
    session: Session, signal: Signal
) -> None:
    broken = signal.model_copy(
        update={
            "source_id": 999,
            "sources": [source(SourceType.TRIP, 999)],
        }
    )
    candidate = correlate_signals(1, [broken])[0]
    with pytest.raises(IntegrityError):
        process_alert(
            session, candidate, estimate(confidence=None), RuleConfig(), DecisionPolicyConfig()
        )
    session.rollback()
    for model in (FraudAlert, DecisionResult, FraudCase, FraudEvidence):
        assert session.scalar(select(func.count()).select_from(model)) == 0


def test_policy_changes_preserve_previous_snapshot(session: Session, signal: Signal) -> None:
    candidate = correlate_signals(1, [signal])[0]
    first = process_alert(session, candidate, estimate(), RuleConfig(), DecisionPolicyConfig())
    changed = DecisionPolicyConfig(version="policy-v2", auto_clear_max_probability=0.01)
    next_record = process_alert(session, candidate, estimate(), RuleConfig(), changed)
    assert next_record.created and next_record.alert.id != first.alert.id
    assert first.alert.decision_result.outcome == DecisionOutcome.AUTO_CLEAR
    assert next_record.alert.decision_result.outcome == DecisionOutcome.HUMAN_REVIEW


def test_legacy_case_can_resume_internal_review(session: Session, signal: Signal) -> None:
    candidate = correlate_signals(1, [signal])[0]
    record = process_alert(
        session, candidate, estimate(confidence=None), RuleConfig(), DecisionPolicyConfig()
    )
    record.case.status = CaseStatus.AWAITING_DRIVER_EXPLANATION
    session.commit()
    start_review(session, record.case.id, "reviewer", "Resume historical case")
    decision = decide_case(session, record.case.id, CaseStatus.DISMISSED, "reviewer", "Verified")
    assert decision.actor_type == DecisionActor.HUMAN
    assert record.case.explanations == []


def test_alert_and_queue_validation(client: TestClient) -> None:
    for path in (
        "/fraud-alerts?outcome=invalid",
        "/review-queue?limit=0",
        "/fraud-alerts?driver_id=0",
    ):
        assert client.get(path).status_code == 422
    assert client.get("/fraud-alerts/999").status_code == 404
