from enum import StrEnum


class FraudType(StrEnum):
    GPS_SPOOFING = "gps_spoofing"
    REPEATED_TRIPS = "repeated_trips"
    SHARED_DEVICE = "shared_device"
    PROMOTION_ABUSE = "promotion_abuse"


class FraudCategory(StrEnum):
    LOCATION_FRAUD = "location_fraud"
    TRIP_FRAUD = "trip_fraud"
    ACCOUNT_FRAUD = "account_fraud"
    INCENTIVE_FRAUD = "incentive_fraud"


FRAUD_TAXONOMY = {
    FraudType.GPS_SPOOFING: FraudCategory.LOCATION_FRAUD,
    FraudType.REPEATED_TRIPS: FraudCategory.TRIP_FRAUD,
    FraudType.SHARED_DEVICE: FraudCategory.ACCOUNT_FRAUD,
    FraudType.PROMOTION_ABUSE: FraudCategory.INCENTIVE_FRAUD,
}


class DecisionOutcome(StrEnum):
    AUTO_CLEAR = "auto_clear"
    AUTO_FRAUD = "auto_fraud"
    HUMAN_REVIEW = "human_review"


class Impact(StrEnum):
    UNKNOWN = "unknown"
    LOW = "low"
    HIGH = "high"
    CRITICAL = "critical"


class DecisionActor(StrEnum):
    HUMAN = "human"
    SYSTEM = "system"


class CaseStatus(StrEnum):
    # DETECTED is the pending exception queue; old explanation states are read-only history.
    DETECTED = "detected"
    UNDER_REVIEW = "under_review"
    AWAITING_DRIVER_EXPLANATION = "awaiting_driver_explanation"
    DRIVER_RESPONDED = "driver_responded"
    CONFIRMED_FRAUD = "confirmed_fraud"
    DISMISSED = "dismissed"


class Severity(StrEnum):
    MEDIUM = "medium"
    HIGH = "high"


class SourceType(StrEnum):
    DRIVER = "driver"
    TRIP = "trip"
    GPS_EVENT = "gps_event"
    DEVICE = "device"
    PROMOTION = "promotion"
