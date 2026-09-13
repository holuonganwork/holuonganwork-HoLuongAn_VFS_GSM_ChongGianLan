import pytest
from app.core.config import RuleConfig
from app.core.enums import CaseStatus
from app.fraud.engine import persist_case
from app.fraud.types import Signal
from app.models.entities import CaseDecision, CaseStatusEvent, Driver, EvidenceSource, FraudEvidence
from app.services.cases import (
    InvalidTransitionError,
    decide_case,
    get_case,
    start_review,
    transition,
)
from sqlalchemy import func, select
from sqlalchemy.orm import Session


def test_case_and_evidence_creation_are_traceable_and_idempotent(
    session: Session, signal: Signal
) -> None:
    case, created = persist_case(
        session,
        1,
        [signal, signal.model_copy(update={"signal": "gps_location_jump"})],
        RuleConfig(),
    )
    assert created and case.risk_score == 30
    session.commit()
    case = get_case(session, case.id)
    assert len(case.evidence) == 2
    assert case.score_breakdown == {"gps_spoofing": 30}
    assert len(case.evidence[0].sources) == 1
    assert case.evidence[0].sources[0].trip_id == 1
    assert case.evidence[0].evidence_data["speed_kmh"] == 999
    again, created = persist_case(
        session,
        1,
        [signal.model_copy(update={"signal": "gps_location_jump"}), signal],
        RuleConfig(),
    )
    assert not created and again.id == case.id
    assert session.scalar(select(func.count()).select_from(FraudEvidence)) == 2


def test_case_and_evidence_rollback_together(session: Session, signal: Signal) -> None:
    case, _ = persist_case(session, 1, [signal], RuleConfig())
    case_id = case.id
    session.rollback()
    assert session.get(type(case), case_id) is None
    assert session.scalar(select(func.count()).select_from(EvidenceSource)) == 0


def test_full_review_flow_preserves_driver_status_and_terminal_state(
    session: Session, signal: Signal
) -> None:
    case, _ = persist_case(session, 1, [signal], RuleConfig())
    session.commit()
    start_review(session, case.id, "reviewer", "Inspect evidence")
    decision = decide_case(
        session, case.id, CaseStatus.DISMISSED, "reviewer", "Signal loss verified"
    )
    session.commit()
    assert decision.reason == "Signal loss verified"
    assert session.get(Driver, 1).status == "active"
    same, created = persist_case(session, 1, [signal], RuleConfig())
    assert not created and same.status == CaseStatus.DISMISSED
    assert session.scalar(select(func.count()).select_from(CaseStatusEvent)) == 2
    assert session.scalar(select(func.count()).select_from(CaseDecision)) == 1
    with pytest.raises(InvalidTransitionError):
        start_review(session, case.id, "reviewer", "Try reopening")
    with pytest.raises(InvalidTransitionError):
        decide_case(session, case.id, CaseStatus.CONFIRMED_FRAUD, "reviewer", "Overwriting")


@pytest.mark.parametrize("initial", list(CaseStatus))
@pytest.mark.parametrize("target", list(CaseStatus))
def test_transition_matrix(
    session: Session, signal: Signal, initial: CaseStatus, target: CaseStatus
) -> None:
    case, _ = persist_case(session, 1, [signal], RuleConfig())
    case.status = initial
    session.flush()
    valid_pairs = {
        ("detected", "under_review"),
        ("under_review", "dismissed"),
        ("under_review", "confirmed_fraud"),
        ("awaiting_driver_explanation", "under_review"),
        ("driver_responded", "under_review"),
    }
    if (initial, target) in valid_pairs:
        transition(session, case, target, "test-reviewer", "Test transition")
        assert case.status == target
    else:
        with pytest.raises(InvalidTransitionError):
            transition(session, case, target, "test-reviewer", "Test transition")
        assert case.status == initial


def test_decision_requires_review_and_final_value(session: Session, signal: Signal) -> None:
    case, _ = persist_case(session, 1, [signal], RuleConfig())
    with pytest.raises(InvalidTransitionError):
        decide_case(session, case.id, CaseStatus.DISMISSED, "reviewer", "Not reviewed")
    with pytest.raises(InvalidTransitionError):
        decide_case(session, case.id, CaseStatus.DETECTED, "reviewer", "Not a decision")
