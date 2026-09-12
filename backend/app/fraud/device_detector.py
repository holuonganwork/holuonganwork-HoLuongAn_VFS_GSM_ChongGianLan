from app.core.config import RuleConfig
from app.core.enums import FraudType, Severity, SourceType
from app.fraud.types import DriverObservation, Signal, source


def detect(observation: DriverObservation, config: RuleConfig) -> list[Signal]:
    signals = []
    for device in sorted(observation.devices, key=lambda item: item.id):
        memberships = sorted(
            (item for item in observation.device_memberships if item.device_id == device.id),
            key=lambda item: item.driver_id,
        )
        driver_ids = sorted({item.driver_id for item in memberships})
        if len(driver_ids) < config.shared_device_min_drivers:
            continue
        signals.append(
            Signal(
                signal="device_shared_by_accounts",
                fraud_type=FraudType.SHARED_DEVICE,
                severity=Severity.MEDIUM,
                description="One device has been observed on multiple distinct driver accounts.",
                source_type=SourceType.DEVICE,
                source_id=device.id,
                details={
                    "device_identifier": device.device_identifier,
                    "driver_count": len(driver_ids),
                    "driver_ids": driver_ids,
                    "related_external_driver_ids": [
                        observation.related_drivers[driver_id].external_driver_id
                        for driver_id in driver_ids
                        if driver_id != observation.driver.id
                    ],
                    "min_drivers": config.shared_device_min_drivers,
                    "memberships": [
                        {
                            "driver_id": item.driver_id,
                            "first_seen_at": item.first_seen_at.isoformat(),
                            "last_seen_at": item.last_seen_at.isoformat(),
                        }
                        for item in memberships
                    ],
                },
                sources=[source(SourceType.DEVICE, device.id)]
                + [source(SourceType.DRIVER, driver_id) for driver_id in driver_ids],
            )
        )
    return signals
