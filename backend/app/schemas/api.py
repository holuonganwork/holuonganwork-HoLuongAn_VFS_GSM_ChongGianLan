from datetime import datetime
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from app.core.enums import CaseStatus, FraudType, Severity, SourceType

ExplanationText = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=10000)
]
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
    created_at: datetime


class StatusEventResponse(ORMResponse):
    id: int
    from_status: CaseStatus
    to_status: CaseStatus
    actor: str
    reason: str
    created_at: datetime


class CaseResponse(ORMResponse):
    id: int
    driver_id: int
    fraud_type: FraudType
    fraud_types: list[FraudType]
    risk_score: int
    score_breakdown: dict[str, int]
    status: CaseStatus
    created_at: datetime
    updated_at: datetime


class CaseDetailResponse(CaseResponse):
    rule_config: dict[str, Any]
    evidence: list[EvidenceResponse]
    explanations: list[ExplanationResponse]
    decisions: list[DecisionResponse]
    status_events: list[StatusEventResponse]


class ExplanationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    explanation: ExplanationText


class ReviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    reviewer: ReviewerText
    reason: ReasonText


class DecisionRequest(ReviewRequest):
    decision: Literal["dismissed", "confirmed_fraud"]
