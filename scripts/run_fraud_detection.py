"""Run processing, detection, alert correlation and decision policy atomically."""

import json
import sys
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.core.config import get_settings  # noqa: E402
from app.core.logging import configure_logging  # noqa: E402
from app.db.session import get_engine  # noqa: E402
from app.fraud.engine import run_detection  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402


def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    with Session(get_engine()) as session, session.begin():
        summary = run_detection(session, settings.fraud_rules, settings.decision_policy)
    print(json.dumps(asdict(summary)))


if __name__ == "__main__":
    main()
