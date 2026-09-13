from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any

from sqlalchemy import (
    CheckConstraint,
    Enum,
    Float,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import (
    FRAUD_TAXONOMY,
    CaseStatus,
    DecisionActor,
    DecisionOutcome,
    FraudCategory,
    FraudType,
    Impact,
    Severity,
    SourceType,
)
from app.db.base import JSON_DATA, Base, UTCDateTime, utc_now


def enum_column(enum: type[StrEnum], name: str) -> Enum:
    return Enum(
        enum,
        native_enum=False,
        create_constraint=True,
        validate_strings=True,
        values_callable=lambda cls: [item.value for item in cls],
        name=name,
    )


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utc_now, onupdate=utc_now)


class Driver(TimestampMixin, Base):
    __tablename__ = "drivers"
    id: Mapped[int] = mapped_column(primary_key=True)
    external_driver_id: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(40), default="active")


class Promotion(Base):
    __tablename__ = "promotions"
    __table_args__ = (
        CheckConstraint("ends_at > starts_at", name="valid_period"),
        CheckConstraint("trip_threshold > 0 AND reward_amount >= 0", name="valid_reward"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(64), unique=True)
    starts_at: Mapped[datetime] = mapped_column(UTCDateTime())
    ends_at: Mapped[datetime] = mapped_column(UTCDateTime())
    trip_threshold: Mapped[int] = mapped_column(Integer)
    reward_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utc_now)


class Trip(Base):
    __tablename__ = "trips"
    __table_args__ = (
        UniqueConstraint("id", "driver_id"),
        CheckConstraint("ended_at > started_at", name="valid_period"),
        CheckConstraint(
            "distance_km >= 0 AND fare_amount >= 0 AND promotion_amount >= 0",
            name="nonnegative_amounts",
        ),
        CheckConstraint(
            "pickup_lat BETWEEN -90 AND 90 AND dropoff_lat BETWEEN -90 AND 90",
            name="valid_latitudes",
        ),
        CheckConstraint(
            "pickup_lng BETWEEN -180 AND 180 AND dropoff_lng BETWEEN -180 AND 180",
            name="valid_longitudes",
        ),
        Index("ix_trips_driver_started", "driver_id", "started_at"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"))
    pickup_lat: Mapped[float] = mapped_column(Float)
    pickup_lng: Mapped[float] = mapped_column(Float)
    dropoff_lat: Mapped[float] = mapped_column(Float)
    dropoff_lng: Mapped[float] = mapped_column(Float)
    started_at: Mapped[datetime] = mapped_column(UTCDateTime())
    ended_at: Mapped[datetime] = mapped_column(UTCDateTime())
    distance_km: Mapped[float] = mapped_column(Float)
    fare_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    promotion_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    promotion_id: Mapped[int | None] = mapped_column(ForeignKey("promotions.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utc_now)


class GPSEvent(Base):
    __tablename__ = "gps_events"
    __table_args__ = (
        ForeignKeyConstraint(["trip_id", "driver_id"], ["trips.id", "trips.driver_id"]),
        CheckConstraint("latitude BETWEEN -90 AND 90", name="valid_latitude"),
        CheckConstraint("longitude BETWEEN -180 AND 180", name="valid_longitude"),
        Index("ix_gps_events_trip_recorded", "trip_id", "recorded_at"),
        Index("ix_gps_events_driver_recorded", "driver_id", "recorded_at"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"))
    trip_id: Mapped[int] = mapped_column(Integer)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    recorded_at: Mapped[datetime] = mapped_column(UTCDateTime())


class Device(Base):
    __tablename__ = "devices"
    id: Mapped[int] = mapped_column(primary_key=True)
    device_identifier: Mapped[str] = mapped_column(String(200), unique=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utc_now)


class DriverDevice(Base):
    __tablename__ = "driver_devices"
    __table_args__ = (
        CheckConstraint("last_seen_at >= first_seen_at", name="valid_period"),
        Index("ix_driver_devices_device_id", "device_id"),
    )
    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"), primary_key=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"), primary_key=True)
    first_seen_at: Mapped[datetime] = mapped_column(UTCDateTime())
    last_seen_at: Mapped[datetime] = mapped_column(UTCDateTime())


class FraudAlert(Base):
    """Immutable correlated detection snapshot, including alerts cleared without a case."""

    __tablename__ = "fraud_alerts"
    __table_args__ = (
        CheckConstraint("risk_score BETWEEN 0 AND 100", name="valid_risk_score"),
        CheckConstraint("fraud_probability BETWEEN 0 AND 1", name="valid_probability"),
        CheckConstraint("confidence BETWEEN 0 AND 1", name="valid_confidence"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"), index=True)
    correlation_key: Mapped[str] = mapped_column(String(64), index=True)
    detection_fingerprint: Mapped[str] = mapped_column(String(64), unique=True)
    fraud_type: Mapped[FraudType] = mapped_column(enum_column(FraudType, "fraud_type"))
    fraud_types: Mapped[list[str]] = mapped_column(JSON_DATA)
    severity: Mapped[Severity] = mapped_column(enum_column(Severity, "severity"))
    risk_score: Mapped[int] = mapped_column(Integer)
    fraud_probability: Mapped[float | None] = mapped_column(Float)
    confidence: Mapped[float | None] = mapped_column(Float)
    impact: Mapped[Impact] = mapped_column(enum_column(Impact, "impact"))
    model_version: Mapped[str] = mapped_column(String(100))
    assessment: Mapped[dict[str, Any]] = mapped_column(JSON_DATA)
    rule_config: Mapped[dict[str, Any]] = mapped_column(JSON_DATA)
    signals: Mapped[list[dict[str, Any]]] = mapped_column(JSON_DATA)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utc_now)
    decision_result: Mapped["DecisionResult"] = relationship(back_populates="alert")

    @property
    def fraud_category(self) -> FraudCategory:
        return FRAUD_TAXONOMY[self.fraud_type]


class DecisionResult(Base):
    __tablename__ = "decision_results"
    id: Mapped[int] = mapped_column(primary_key=True)
    alert_id: Mapped[int] = mapped_column(ForeignKey("fraud_alerts.id"), unique=True)
    outcome: Mapped[DecisionOutcome] = mapped_column(
        enum_column(DecisionOutcome, "decision_outcome"), index=True
    )
    reason: Mapped[str] = mapped_column(Text)
    policy_version: Mapped[str] = mapped_column(String(100))
    policy_config: Mapped[dict[str, Any]] = mapped_column(JSON_DATA)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utc_now)
    alert: Mapped[FraudAlert] = relationship(back_populates="decision_result")


class FraudCase(TimestampMixin, Base):
    __tablename__ = "fraud_cases"
    __table_args__ = (
        CheckConstraint("risk_score BETWEEN 0 AND 100", name="valid_risk_score"),
        Index("ix_fraud_cases_status_risk", "status", "risk_score"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    # Null for investigations created before the architecture upgrade.
    alert_id: Mapped[int | None] = mapped_column(ForeignKey("fraud_alerts.id"), unique=True)
    alert: Mapped[FraudAlert | None] = relationship()
    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"), index=True)
    fraud_type: Mapped[FraudType] = mapped_column(enum_column(FraudType, "fraud_type"), index=True)
    fraud_types: Mapped[list[str]] = mapped_column(JSON_DATA)
    risk_score: Mapped[int] = mapped_column(Integer)
    score_breakdown: Mapped[dict[str, int]] = mapped_column(JSON_DATA)
    rule_config: Mapped[dict[str, Any]] = mapped_column(JSON_DATA)
    detection_fingerprint: Mapped[str] = mapped_column(String(64), unique=True)
    status: Mapped[CaseStatus] = mapped_column(
        enum_column(CaseStatus, "case_status"), default=CaseStatus.DETECTED
    )
    evidence: Mapped[list["FraudEvidence"]] = relationship(
        back_populates="case", order_by="FraudEvidence.id"
    )
    explanations: Mapped[list["DriverExplanation"]] = relationship(order_by="DriverExplanation.id")
    decisions: Mapped[list["CaseDecision"]] = relationship(order_by="CaseDecision.id")
    status_events: Mapped[list["CaseStatusEvent"]] = relationship(order_by="CaseStatusEvent.id")

    @property
    def fraud_category(self) -> FraudCategory:
        return FRAUD_TAXONOMY[self.fraud_type]


class FraudEvidence(Base):
    __tablename__ = "fraud_evidences"
    __table_args__ = (CheckConstraint("score BETWEEN 0 AND 100", name="valid_score"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("fraud_cases.id"), index=True)
    fraud_type: Mapped[FraudType] = mapped_column(enum_column(FraudType, "fraud_type"), index=True)
    evidence_type: Mapped[str] = mapped_column(String(100))
    source_type: Mapped[SourceType] = mapped_column(enum_column(SourceType, "source_type"))
    source_id: Mapped[int] = mapped_column(Integer)
    severity: Mapped[Severity] = mapped_column(enum_column(Severity, "severity"))
    score: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(Text)
    evidence_data: Mapped[dict[str, Any]] = mapped_column(JSON_DATA)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utc_now)
    case: Mapped[FraudCase] = relationship(back_populates="evidence")
    sources: Mapped[list["EvidenceSource"]] = relationship(order_by="EvidenceSource.id")


class EvidenceSource(Base):
    """Typed FKs prevent loss of raw data referenced by investigation evidence."""

    __tablename__ = "evidence_sources"
    __table_args__ = (
        UniqueConstraint("evidence_id", "source_type", "source_id"),
        CheckConstraint(
            "(CASE WHEN driver_id IS NULL THEN 0 ELSE 1 END + "
            "CASE WHEN trip_id IS NULL THEN 0 ELSE 1 END + "
            "CASE WHEN gps_event_id IS NULL THEN 0 ELSE 1 END + "
            "CASE WHEN device_id IS NULL THEN 0 ELSE 1 END + "
            "CASE WHEN promotion_id IS NULL THEN 0 ELSE 1 END) = 1",
            name="one_source",
        ),
        CheckConstraint(
            "(source_type = 'driver' AND driver_id IS NOT NULL AND source_id = driver_id) OR "
            "(source_type = 'trip' AND trip_id IS NOT NULL AND source_id = trip_id) OR "
            "(source_type = 'gps_event' AND gps_event_id IS NOT NULL "
            "AND source_id = gps_event_id) OR "
            "(source_type = 'device' AND device_id IS NOT NULL AND source_id = device_id) OR "
            "(source_type = 'promotion' AND promotion_id IS NOT NULL AND source_id = promotion_id)",
            name="source_matches",
        ),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    evidence_id: Mapped[int] = mapped_column(ForeignKey("fraud_evidences.id"), index=True)
    source_type: Mapped[SourceType] = mapped_column(enum_column(SourceType, "source_type"))
    source_id: Mapped[int] = mapped_column(Integer)
    driver_id: Mapped[int | None] = mapped_column(ForeignKey("drivers.id"), index=True)
    trip_id: Mapped[int | None] = mapped_column(ForeignKey("trips.id"), index=True)
    gps_event_id: Mapped[int | None] = mapped_column(ForeignKey("gps_events.id"), index=True)
    device_id: Mapped[int | None] = mapped_column(ForeignKey("devices.id"), index=True)
    promotion_id: Mapped[int | None] = mapped_column(ForeignKey("promotions.id"), index=True)


class DriverExplanation(Base):
    """Deprecated storage retained for historical investigations; no write workflow."""

    __tablename__ = "driver_explanations"
    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("fraud_cases.id"), index=True)
    explanation: Mapped[str] = mapped_column(Text)
    attachment_metadata: Mapped[list[dict[str, Any]]] = mapped_column(JSON_DATA, default=list)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utc_now)


class CaseDecision(Base):
    __tablename__ = "case_decisions"
    __table_args__ = (
        CheckConstraint("decision IN ('confirmed_fraud', 'dismissed')", name="terminal_decision"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("fraud_cases.id"), unique=True)
    decision: Mapped[CaseStatus] = mapped_column(enum_column(CaseStatus, "decision"))
    reviewer: Mapped[str] = mapped_column(String(200))
    reason: Mapped[str] = mapped_column(Text)
    actor_type: Mapped[DecisionActor] = mapped_column(
        enum_column(DecisionActor, "decision_actor"),
        default=DecisionActor.HUMAN,
        server_default="human",
    )
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utc_now)


class CaseStatusEvent(Base):
    __tablename__ = "case_status_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("fraud_cases.id"), index=True)
    from_status: Mapped[CaseStatus] = mapped_column(enum_column(CaseStatus, "from_status"))
    to_status: Mapped[CaseStatus] = mapped_column(enum_column(CaseStatus, "to_status"))
    actor: Mapped[str] = mapped_column(String(200))
    reason: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utc_now)
