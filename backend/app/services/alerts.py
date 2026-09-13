from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.enums import DecisionOutcome
from app.models.entities import DecisionResult, FraudAlert
from app.services.cases import NotFoundError


def list_alerts(
    session: Session,
    *,
    outcome: DecisionOutcome | None = None,
    driver_id: int | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[FraudAlert]:
    query = select(FraudAlert).options(selectinload(FraudAlert.decision_result))
    if outcome is not None:
        query = query.where(FraudAlert.decision_result.has(DecisionResult.outcome == outcome))
    if driver_id is not None:
        query = query.where(FraudAlert.driver_id == driver_id)
    return list(session.scalars(query.order_by(FraudAlert.id).offset(offset).limit(limit)))


def get_alert(session: Session, alert_id: int) -> FraudAlert:
    alert = session.scalar(
        select(FraudAlert)
        .where(FraudAlert.id == alert_id)
        .options(selectinload(FraudAlert.decision_result))
    )
    if alert is None:
        raise NotFoundError("Fraud alert not found")
    return alert
