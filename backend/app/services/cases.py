import logging

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.enums import CaseStatus, FraudType
from app.models.entities import (
    CaseDecision,
    CaseStatusEvent,
    DriverExplanation,
    FraudCase,
    FraudEvidence,
)

logger = logging.getLogger(__name__)


class NotFoundError(Exception):
    pass


class InvalidTransitionError(Exception):
    pass


ALLOWED_TRANSITIONS: dict[CaseStatus, set[CaseStatus]] = {
    CaseStatus.DETECTED: {CaseStatus.UNDER_REVIEW},
    CaseStatus.UNDER_REVIEW: {
        CaseStatus.AWAITING_DRIVER_EXPLANATION,
        CaseStatus.DISMISSED,
        CaseStatus.CONFIRMED_FRAUD,
    },
    CaseStatus.AWAITING_DRIVER_EXPLANATION: {CaseStatus.DRIVER_RESPONDED},
    CaseStatus.DRIVER_RESPONDED: {
        CaseStatus.UNDER_REVIEW,
        CaseStatus.DISMISSED,
        CaseStatus.CONFIRMED_FRAUD,
    },
    CaseStatus.DISMISSED: set(),
    CaseStatus.CONFIRMED_FRAUD: set(),
}


def get_case(session: Session, case_id: int, *, lock: bool = False) -> FraudCase:
    query = (
        select(FraudCase)
        .where(FraudCase.id == case_id)
        .options(
            selectinload(FraudCase.evidence).selectinload(FraudEvidence.sources),
            selectinload(FraudCase.explanations),
            selectinload(FraudCase.decisions),
            selectinload(FraudCase.status_events),
        )
    )
    if lock:
        query = query.with_for_update().execution_options(populate_existing=True)
    case = session.scalar(query)
    if case is None:
        raise NotFoundError("Fraud case not found")
    return case


def list_cases(
    session: Session,
    *,
    fraud_type: FraudType | None = None,
    status: CaseStatus | None = None,
    min_risk_score: int | None = None,
    driver_id: int | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[FraudCase]:
    query = select(FraudCase)
    if fraud_type is not None:
        # Match any contributing category, including secondary signals.
        query = query.where(FraudCase.evidence.any(FraudEvidence.fraud_type == fraud_type))
    if status is not None:
        query = query.where(FraudCase.status == status)
    if min_risk_score is not None:
        query = query.where(FraudCase.risk_score >= min_risk_score)
    if driver_id is not None:
        query = query.where(FraudCase.driver_id == driver_id)
    return list(session.scalars(query.order_by(FraudCase.id).offset(offset).limit(limit)))


def transition(
    session: Session, case: FraudCase, target: CaseStatus, actor: str, reason: str
) -> None:
    if target not in ALLOWED_TRANSITIONS[case.status]:
        raise InvalidTransitionError(f"Cannot transition from {case.status} to {target}")
    event = CaseStatusEvent(
        case_id=case.id, from_status=case.status, to_status=target, actor=actor, reason=reason
    )
    case.status_events.append(event)
    case.status = target
    session.flush()
    logger.info("Case %s transitioned to %s", case.id, target)


def start_review(session: Session, case_id: int, reviewer: str, reason: str) -> FraudCase:
    case = get_case(session, case_id, lock=True)
    transition(session, case, CaseStatus.UNDER_REVIEW, reviewer, reason)
    return case


def request_explanation(session: Session, case_id: int, reviewer: str, reason: str) -> FraudCase:
    case = get_case(session, case_id, lock=True)
    transition(session, case, CaseStatus.AWAITING_DRIVER_EXPLANATION, reviewer, reason)
    return case


def submit_explanation(session: Session, case_id: int, explanation: str) -> DriverExplanation:
    case = get_case(session, case_id, lock=True)
    transition(
        session,
        case,
        CaseStatus.DRIVER_RESPONDED,
        f"driver:{case.driver_id}",
        "Driver explanation submitted",
    )
    record = DriverExplanation(case_id=case.id, explanation=explanation)
    case.explanations.append(record)
    session.flush()
    return record


def decide_case(
    session: Session, case_id: int, decision: CaseStatus, reviewer: str, reason: str
) -> CaseDecision:
    if decision not in {CaseStatus.DISMISSED, CaseStatus.CONFIRMED_FRAUD}:
        raise InvalidTransitionError("A final decision must be dismissed or confirmed_fraud")
    case = get_case(session, case_id, lock=True)
    transition(session, case, decision, reviewer, reason)
    record = CaseDecision(case_id=case.id, decision=decision, reviewer=reviewer, reason=reason)
    case.decisions.append(record)
    session.flush()
    return record
