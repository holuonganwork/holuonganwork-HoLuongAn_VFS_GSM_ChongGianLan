"""Generate reproducible source data and load it into an empty migrated database."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.core.config import get_settings  # noqa: E402
from app.core.logging import configure_logging  # noqa: E402
from app.db.session import get_engine  # noqa: E402
from app.services.synthetic import generate_dataset, load_dataset  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--drivers", type=int, default=100)
    parser.add_argument("--trips-per-driver", type=int, default=50)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data" / "generated")
    parser.add_argument(
        "--export-only", action="store_true", help="Write JSON without database access"
    )
    args = parser.parse_args()
    configure_logging(get_settings().log_level)
    try:
        dataset = generate_dataset(args.seed, args.drivers, args.trips_per_driver)
        if not args.export_only:
            with Session(get_engine()) as session, session.begin():
                load_dataset(session, dataset)
        manifest = dataset.export(args.output_dir)
    except ValueError as exc:
        parser.exit(1, f"{exc}\n")
    print(json.dumps({"loaded": not args.export_only, **manifest}, indent=2))


if __name__ == "__main__":
    main()
