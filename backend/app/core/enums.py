from enum import StrEnum


class FraudType(StrEnum):
    GPS_SPOOFING = "gps_spoofing"
    REPEATED_TRIPS = "repeated_trips"
    SHARED_DEVICE = "shared_device"
    PROMOTION_ABUSE = "promotion_abuse"


class CaseStatus(StrEnum):
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
