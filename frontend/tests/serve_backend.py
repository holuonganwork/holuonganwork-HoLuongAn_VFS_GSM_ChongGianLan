"""Run the actual API with isolated synthetic data for frontend browser checks only."""

from collections.abc import Iterator

import uvicorn
from app.db.base import Base
from app.db.session import get_session
from app.fraud.engine import run_detection
from app.main import app
from app.services.synthetic import generate_dataset, load_dataset
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

# This test process never calls get_engine() or connects to the configured PostgreSQL DB.
engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
Base.metadata.create_all(engine)
with Session(engine) as session, session.begin():
    load_dataset(session, generate_dataset(seed=42))
    run_detection(session)


def test_session() -> Iterator[Session]:
    with Session(engine, expire_on_commit=False) as session:
        yield session


app.dependency_overrides[get_session] = test_session

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8751, log_level="warning")
