from decimal import Decimal
from typing import Any

from fastapi.encoders import jsonable_encoder
from sqlalchemy import inspect, select
from sqlalchemy.orm import Session

from app.models.entities import (
    Device,
    Driver,
    DriverDevice,
    EvidenceSource,
    GPSEvent,
    Promotion,
    Trip,
)
from app.services.cases import NotFoundError, get_case

SOURCE_MODELS = {
    "driver": Driver,
    "trip": Trip,
    "gps_event": GPSEvent,
    "device": Device,
    "promotion": Promotion,
}


def list_drivers(session: Session, limit: int, offset: int) -> list[Driver]:
    return list(session.scalars(select(Driver).order_by(Driver.id).offset(offset).limit(limit)))


def get_driver(session: Session, driver_id: int) -> Driver:
    driver = session.get(Driver, driver_id)
    if driver is None:
        raise NotFoundError("Driver not found")
    return driver


def record_data(record: Any) -> dict[str, Any]:
    return jsonable_encoder(
        {column.key: getattr(record, column.key) for column in inspect(type(record)).columns},
        custom_encoder={Decimal: str},
    )


def evidence_sources(session: Session, case_id: int, evidence_id: int) -> list[dict[str, Any]]:
    case = get_case(session, case_id)
    if not any(item.id == evidence_id for item in case.evidence):
        raise NotFoundError("Evidence not found in this case")
    refs = session.scalars(
        select(EvidenceSource)
        .where(EvidenceSource.evidence_id == evidence_id)
        .order_by(EvidenceSource.id)
    )
    result = []
    for ref in refs:
        record = session.get(SOURCE_MODELS[ref.source_type], ref.source_id)
        if record is None:
            raise NotFoundError("Referenced source record not found")
        data = record_data(record)
        if ref.source_type == "device":
            data["driver_memberships"] = [
                record_data(item)
                for item in session.scalars(
                    select(DriverDevice)
                    .where(DriverDevice.device_id == ref.source_id)
                    .order_by(DriverDevice.driver_id)
                )
            ]
        result.append({"source_type": ref.source_type, "source_id": ref.source_id, "data": data})
    return result
