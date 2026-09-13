from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.enums import CaseStatus, DecisionOutcome, FraudType
from app.db.session import get_session
from app.schemas.api import (
    AlertDetailResponse,
    AlertResponse,
    CaseDetailResponse,
    CaseResponse,
    DecisionRequest,
    DecisionResponse,
    DriverResponse,
    EvidenceResponse,
    ReviewRequest,
    SourceDataResponse,
)
from app.services import alerts, cases, sources

router = APIRouter()
DB = Annotated[Session, Depends(get_session)]
RecordID = Annotated[int, Path(gt=0)]
Limit = Annotated[int, Query(ge=1, le=200)]
Offset = Annotated[int, Query(ge=0)]


@router.get("/health", tags=["operations"])
def health(session: DB) -> dict[str, str]:
    try:
        session.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc
    return {"status": "ok"}


@router.get("/drivers", response_model=list[DriverResponse], tags=["drivers"])
def list_drivers(session: DB, limit: Limit = 50, offset: Offset = 0) -> object:
    return sources.list_drivers(session, limit, offset)


@router.get("/drivers/{driver_id}", response_model=DriverResponse, tags=["drivers"])
def get_driver(driver_id: RecordID, session: DB) -> object:
    return sources.get_driver(session, driver_id)


@router.get("/fraud-cases", response_model=list[CaseResponse], tags=["cases"])
def list_cases(
    session: DB,
    fraud_type: FraudType | None = None,
    status: CaseStatus | None = None,
    min_risk_score: Annotated[int | None, Query(ge=0, le=100)] = None,
    driver_id: Annotated[int | None, Query(gt=0)] = None,
    limit: Limit = 50,
    offset: Offset = 0,
) -> object:
    return cases.list_cases(
        session,
        fraud_type=fraud_type,
        status=status,
        min_risk_score=min_risk_score,
        driver_id=driver_id,
        limit=limit,
        offset=offset,
    )


@router.get("/fraud-cases/{case_id}", response_model=CaseDetailResponse, tags=["cases"])
def get_case(case_id: RecordID, session: DB) -> object:
    return cases.get_case(session, case_id)


@router.get(
    "/fraud-cases/{case_id}/evidence", response_model=list[EvidenceResponse], tags=["evidence"]
)
def get_evidence(case_id: RecordID, session: DB) -> object:
    return cases.get_case(session, case_id).evidence


@router.get(
    "/fraud-cases/{case_id}/evidence/{evidence_id}/sources",
    response_model=list[SourceDataResponse],
    tags=["evidence"],
)
def get_evidence_sources(case_id: RecordID, evidence_id: RecordID, session: DB) -> object:
    return sources.evidence_sources(session, case_id, evidence_id)


@router.post("/fraud-cases/{case_id}/review", response_model=CaseDetailResponse, tags=["review"])
def start_review(case_id: RecordID, body: ReviewRequest, session: DB) -> object:
    return cases.start_review(session, case_id, body.reviewer, body.reason)


@router.get("/review-queue", response_model=list[CaseResponse], tags=["review"])
def review_queue(session: DB, limit: Limit = 50, offset: Offset = 0) -> object:
    return cases.review_queue(session, limit, offset)


@router.get("/fraud-alerts", response_model=list[AlertResponse], tags=["alerts"])
def list_alerts(
    session: DB,
    outcome: DecisionOutcome | None = None,
    driver_id: Annotated[int | None, Query(gt=0)] = None,
    limit: Limit = 50,
    offset: Offset = 0,
) -> object:
    return alerts.list_alerts(
        session,
        outcome=outcome,
        driver_id=driver_id,
        limit=limit,
        offset=offset,
    )


@router.get("/fraud-alerts/{alert_id}", response_model=AlertDetailResponse, tags=["alerts"])
def get_alert(alert_id: RecordID, session: DB) -> object:
    return alerts.get_alert(session, alert_id)


@router.post(
    "/fraud-cases/{case_id}/decision",
    response_model=DecisionResponse,
    status_code=201,
    tags=["review"],
)
def submit_decision(case_id: RecordID, body: DecisionRequest, session: DB) -> object:
    return cases.decide_case(
        session, case_id, CaseStatus(body.decision), body.reviewer, body.reason
    )
