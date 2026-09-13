"""Contracts shared by synchronous detection and future model/worker adapters."""

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import Impact
from app.fraud.types import Signal


class Assessment(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", allow_inf_nan=False)

    risk_score: int = Field(ge=0, le=100)
    fraud_probability: float | None = Field(default=None, ge=0, le=1)
    confidence: float | None = Field(default=None, ge=0, le=1)
    impact: Impact = Impact.UNKNOWN
    conflicting_signals: bool = False
    model_version: str = Field(min_length=1, max_length=100)


class AlertCandidate(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    driver_id: int = Field(gt=0)
    correlation_key: str
    signals: list[Signal] = Field(min_length=1)
