"""Existing bounded batch loader. Streaming ingestion is a later adapter."""

from collections import defaultdict
from collections.abc import Iterator

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.fraud.types import DriverObservation
from app.models.entities import Device, Driver, DriverDevice, GPSEvent, Promotion, Trip


def load_observations(session: Session) -> Iterator[DriverObservation]:
    drivers = {driver.id: driver for driver in session.scalars(select(Driver).order_by(Driver.id))}
    trips: dict[int, list[Trip]] = defaultdict(list)
    for trip in session.scalars(select(Trip).order_by(Trip.id)):
        trips[trip.driver_id].append(trip)
    gps: dict[int, list[GPSEvent]] = defaultdict(list)
    for event in session.scalars(select(GPSEvent).order_by(GPSEvent.id)):
        gps[event.driver_id].append(event)
    devices = {device.id: device for device in session.scalars(select(Device))}
    memberships = list(session.scalars(select(DriverDevice)))
    by_device: dict[int, list[DriverDevice]] = defaultdict(list)
    by_driver: dict[int, list[int]] = defaultdict(list)
    for membership in memberships:
        by_device[membership.device_id].append(membership)
        by_driver[membership.driver_id].append(membership.device_id)
    promotions = {promo.id: promo for promo in session.scalars(select(Promotion))}
    for driver in drivers.values():
        device_ids = sorted(by_driver[driver.id])
        yield DriverObservation(
            driver=driver,
            trips=trips[driver.id],
            gps_events=gps[driver.id],
            devices=[devices[device_id] for device_id in device_ids],
            device_memberships=[item for device_id in device_ids for item in by_device[device_id]],
            related_drivers=drivers,
            promotions=promotions,
        )
