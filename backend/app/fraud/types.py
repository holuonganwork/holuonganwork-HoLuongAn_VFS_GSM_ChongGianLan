from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict, JsonValue, computed_field

from app.core.enums import FRAUD_TAXONOMY, FraudCategory, FraudType, Severity, SourceType
from app.models.entities import Device, Driver, DriverDevice, GPSEvent, Promotion, Trip


class SourceReference(BaseModel):
    model_config = ConfigDict(frozen=True)
    source_type: SourceType
    source_id: int


class Signal(BaseModel):
    model_config = ConfigDict(frozen=True)
    signal: str
    fraud_type: FraudType
    severity: Severity
    description: str
    source_type: SourceType
    source_id: int
    details: dict[str, JsonValue]
    sources: list[SourceReference]

    @computed_field
    @property
    def fraud_category(self) -> FraudCategory:
        return FRAUD_TAXONOMY[self.fraud_type]


@dataclass(frozen=True)
class DriverObservation:
    driver: Driver
    trips: list[Trip]
    gps_events: list[GPSEvent]
    devices: list[Device]
    device_memberships: list[DriverDevice]
    related_drivers: dict[int, Driver]
    promotions: dict[int, Promotion]


def source(kind: SourceType, identifier: int) -> SourceReference:
    return SourceReference(source_type=kind, source_id=identifier)
