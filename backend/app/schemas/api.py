from datetime import datetime
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from app.core.enums import (
    CaseStatus,
    DecisionActor,
    DecisionOutcome,
    FraudCategory,
    FraudType,
    Impact,
    Severity,
    SourceType,
)
from app.fraud.contracts import Assessment
from app.fraud.types import Signal

ReasonText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=4000)]
ReviewerText = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)
]


class ORMResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class DriverResponse(ORMResponse):
    id: int
    external_driver_id: str
    name: str
    status: str
    created_at: datetime
    updated_at: datetime


class SourceResponse(ORMResponse):
    source_type: SourceType
    source_id: int


class SourceDataResponse(SourceResponse):
    data: dict[str, Any]


class EvidenceResponse(ORMResponse):
    id: int
    case_id: int
    fraud_type: FraudType
    evidence_type: str
    source_type: SourceType
    source_id: int
    severity: Severity
    score: int = Field(description="Category weight; counted once per category in the case score")
    description: str
    evidence_data: dict[str, Any]
    sources: list[SourceResponse]
    created_at: datetime


class ExplanationResponse(ORMResponse):
    id: int
    case_id: int
    explanation: str
    attachment_metadata: list[dict[str, Any]]
    created_at: datetime


class DecisionResponse(ORMResponse):
    id: int
    case_id: int
    decision: CaseStatus
    reviewer: str
    reason: str
    actor_type: DecisionActor
    created_at: datetime


class StatusEventResponse(ORMResponse):
    id: int
    from_status: CaseStatus
    to_status: CaseStatus
    actor: str
    reason: str
    created_at: datetime


class PolicyDecisionResponse(ORMResponse):
    id: int
    alert_id: int
    outcome: DecisionOutcome
    reason: str
    policy_version: str
    policy_config: dict[str, Any]
    created_at: datetime


class AlertResponse(ORMResponse):
    id: int
    driver_id: int
    correlation_key: str
    fraud_category: FraudCategory
    fraud_type: FraudType
    fraud_types: list[FraudType]
    severity: Severity
    risk_score: int
    fraud_probability: float | None
    confidence: float | None
    impact: Impact
    model_version: str
    decision_result: PolicyDecisionResponse
    created_at: datetime


class AlertDetailResponse(AlertResponse):
    detection_fingerprint: str
    assessment: Assessment
    rule_config: dict[str, Any]
    signals: list[Signal]


class CaseResponse(ORMResponse):
    id: int
    driver_id: int
    alert_id: int | None
    fraud_category: FraudCategory
    fraud_type: FraudType
    fraud_types: list[FraudType]
    risk_score: int
    score_breakdown: dict[str, int]
    status: CaseStatus
    created_at: datetime
    updated_at: datetime


class CaseDetailResponse(CaseResponse):
    alert: AlertResponse | None
    rule_config: dict[str, Any]
    evidence: list[EvidenceResponse]
    explanations: list[ExplanationResponse] = Field(description="Read-only legacy history")
    decisions: list[DecisionResponse]
    status_events: list[StatusEventResponse]


class ReviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    reviewer: ReviewerText
    reason: ReasonText


class DecisionRequest(ReviewRequest):
    decision: Literal["dismissed", "confirmed_fraud"]
