from datetime import datetime

import pytest
from app.core.config import RuleConfig
from app.fraud.engine import persist_case
from app.fraud.types import Signal
from app.models.entities import Driver, EvidenceSource, GPSEvent, Trip
from conftest import TIME
from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError, StatementError
from sqlalchemy.orm import Session


def test_gps_cannot_reference_another_drivers_trip(session: Session) -> None:
    session.add(Driver(id=2, external_driver_id="D002", name="Other"))
    session.flush()
    session.add(GPSEvent(driver_id=2, trip_id=1, latitude=10, longitude=106, recorded_at=TIME))
    with pytest.raises(IntegrityError):
        session.flush()


def test_referenced_source_cannot_be_deleted(session: Session, signal: Signal) -> None:
    persist_case(session, 1, [signal], RuleConfig())
    session.commit()
    with pytest.raises(IntegrityError):
        session.execute(delete(Trip).where(Trip.id == 1))


def test_source_type_must_match_fk(session: Session, signal: Signal) -> None:
    case, _ = persist_case(session, 1, [signal], RuleConfig())
    session.add(
        EvidenceSource(
            evidence_id=case.evidence[0].id, source_type="driver", source_id=1, trip_id=1
        )
    )
    with pytest.raises(IntegrityError):
        session.flush()


def test_naive_timestamps_rejected(session: Session) -> None:
    session.get(Trip, 1).started_at = datetime(2026, 1, 1)
    with pytest.raises(StatementError, match="timezone-aware"):
        session.flush()
