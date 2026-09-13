from functools import lru_cache
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.enums import FraudType


class RuleConfig(BaseModel):
    """Example thresholds for synthetic data, not validated production thresholds."""

    model_config = ConfigDict(extra="forbid", frozen=True, allow_inf_nan=False)
    version: str = "demo-v1"
    gps_max_speed_kmh: float = Field(default=180, gt=0)
    gps_jump_distance_km: float = Field(default=5, gt=0)
    gps_jump_seconds: float = Field(default=60, gt=0)
    gps_min_distance_km: float = Field(default=0.1, gt=0)
    repeat_radius_km: float = Field(default=0.2, gt=0)
    repeat_window_hours: float = Field(default=24, gt=0)
    repeat_min_trips: int = Field(default=8, ge=2)
    repeat_max_distance_km: float = Field(default=1, gt=0)
    repeat_max_duration_seconds: float = Field(default=300, gt=0)
    shared_device_min_drivers: int = Field(default=3, ge=2)
    promotion_min_trips: int = Field(default=10, ge=2)
    promotion_min_ratio: float = Field(default=0.8, gt=0, le=1)
    promotion_min_short_ratio: float = Field(default=0.8, gt=0, le=1)
    weights: dict[FraudType, Annotated[int, Field(strict=True, ge=0, le=100)]] = Field(
        default_factory=lambda: {
            FraudType.GPS_SPOOFING: 30,
            FraudType.REPEATED_TRIPS: 25,
            FraudType.SHARED_DEVICE: 25,
            FraudType.PROMOTION_ABUSE: 20,
        }
    )

    @model_validator(mode="after")
    def valid_weights(self) -> "RuleConfig":
        if set(self.weights) != set(FraudType):
            raise ValueError("weights must specify every fraud category")
        return self


class DecisionPolicyConfig(BaseModel):
    """Scaffold policy thresholds; calibrate before supplying production model estimates."""

    model_config = ConfigDict(extra="forbid", frozen=True, allow_inf_nan=False)
    version: str = Field(default="policy-v1", min_length=1, max_length=100)
    auto_clear_max_probability: float = Field(default=0.1, ge=0, le=1)
    auto_clear_max_risk: int = Field(default=20, ge=0, le=100)
    auto_fraud_min_probability: float = Field(default=0.95, ge=0, le=1)
    min_confidence: float = Field(default=0.9, ge=0, le=1)

    @model_validator(mode="after")
    def ordered_thresholds(self) -> "DecisionPolicyConfig":
        if self.auto_clear_max_probability >= self.auto_fraud_min_probability:
            raise ValueError("Automatic clear and fraud thresholds must not overlap")
        return self


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "postgresql+psycopg://fraud@localhost:5432/fraud_investigation"
    log_level: str = "INFO"
    fraud_rules: RuleConfig = Field(default_factory=RuleConfig)
    decision_policy: DecisionPolicyConfig = Field(default_factory=DecisionPolicyConfig)


@lru_cache
def get_settings() -> Settings:
    return Settings()
