# Driver Fraud Investigation System

Hệ thống phân tích dấu hiệu gian lận của tài xế và lưu bằng chứng để tài xế và đội kiểm soát
phối hợp giải trình, xác minh và đưa ra quyết định.

Milestone 1 is a local backend for explainable driver anomaly detection and human investigation.
It preserves original source references, numeric evidence, score contributions, driver explanations,
and reviewer decisions. **An automated score never suspends a driver or confirms fraud.**

## Architecture and stack

```text
Trips / GPS / devices / promotions
    -> four rule detectors -> category scoring -> cases + traceable evidence
    -> human review -> driver explanation -> reviewer decision
```

One Python 3.11+ FastAPI application, PostgreSQL 16, SQLAlchemy 2, Alembic, Pydantic 2,
Pytest, Docker and Docker Compose. Detectors are separate from the API and database writes.
There is no LLM, broker, Redis, Kubernetes, or automatic enforcement.

See [architecture](docs/architecture.md), [rule definitions](docs/fraud-rules.md),
[data model](docs/data-model.md), and [implementation contract](docs/implementation-plan.md).
The completed local checks are recorded in [verification](docs/verification.md).

## Quick start with Docker

Prerequisites: Docker Engine or Docker Desktop running with Linux containers, Docker Compose v2,
and available local ports 5432 and 8000. Run every command below from the repository root.

Copy `.env.example` to `.env` (`cp .env.example .env` on Linux/macOS or
`Copy-Item .env.example .env` in PowerShell). The supplied password is a local development example.
Choose a URL-safe password and keep `POSTGRES_PASSWORD` and the host `DATABASE_URL` consistent.
`.env` is ignored by Git and excluded from the image.

```bash
docker compose up -d --build
docker compose exec backend alembic -c backend/alembic.ini upgrade head
docker compose exec backend python scripts/generate_data.py --seed 42
docker compose exec backend python scripts/run_fraud_detection.py
```

Open **http://localhost:8000/docs** for the interactive API; `/health` checks database connectivity.
Migration is an explicit step: the application does not call `create_all()` or seed on startup.
Source code and generated artifacts are mounted from the repository. After editing application
code, run `docker compose restart backend`; after dependency changes, rebuild with `--build`.

Generated data is written to `data/generated/dataset.json`; `manifest.json` contains counts,
a SHA-256 digest, and source-linked ground truth. The default dataset contains **100 drivers,
5,000 trips, 30,000 GPS events, 101 devices, 103 driver-device associations, and one promotion**.
The timestamps are fixed in January 2026 and all records are synthetic.

With seed 42 and default rule settings, the expected investigations are:

| Driver | Contributing categories | Risk |
| --- | --- | ---: |
| D001 | GPS spoofing / impossible movement | 30 |
| D014 | Repeated short trips | 25 |
| D027 | Shared device | 25 |
| D028 | Shared device with D027 and D029 | 25 |
| D029 | Shared device with D027 and D028 | 25 |
| D050 | Repeated trips + promotion abuse | 45 |

This produces six cases and eight evidence records. These results describe injected fixtures,
not production detection accuracy. A second identical detection run creates zero new cases.

The generator **requires an empty, migrated application database** and refuses to overwrite data.
Use a separate database for a fresh experiment. For repeatable exports without database access:

```bash
python scripts/generate_data.py --seed 42 --export-only
```

The same seed and generator parameters produce byte-identical dataset JSON and the same hash.
Operational timestamps on subsequently created cases and review actions reflect actual execution time.
Optional size controls are `--drivers` (minimum 50) and `--trips-per-driver` (minimum 12).

## Run Python on the host

Python 3.11+ is required. PostgreSQL can still run in Compose:

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell instead:
# .\.venv\Scripts\Activate.ps1
python -m pip install -r backend/requirements-dev.txt
docker compose up -d db
alembic -c backend/alembic.ini upgrade head
python scripts/generate_data.py --seed 42
python scripts/run_fraud_detection.py
uvicorn app.main:app --app-dir backend --reload
```

Use this host API startup instead of the Compose backend if port 8000 is already occupied.
`DATABASE_URL` is read from `.env` or the environment. Compose overrides it to use the `db` hostname;
host commands use `localhost`. Avoid printing database URLs into shared logs.

## Inspect evidence and review a case

`driver_id` and `case_id` are integer database keys. `external_driver_id` is the business identifier
such as D001; it is returned by `/drivers`. Use `/fraud-cases?driver_id=1` to find its cases rather
than assuming case IDs equal driver IDs. All list endpoints accept `limit` (1–200) and `offset`.

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/drivers` | List drivers |
| GET | `/drivers/{driver_id}` | Driver information |
| GET | `/fraud-cases` | Filter by `fraud_type`, `status`, `min_risk_score`, `driver_id` |
| GET | `/fraud-cases/{case_id}` | Case, contributions, rule snapshot, evidence, review history |
| GET | `/fraud-cases/{case_id}/evidence` | All evidence for the case |
| GET | `/fraud-cases/{case_id}/evidence/{evidence_id}/sources` | Original referenced source records |
| POST | `/fraud-cases/{case_id}/review` | Start human review |
| POST | `/fraud-cases/{case_id}/request-explanation` | Request a driver response |
| POST | `/fraud-cases/{case_id}/explanation` | Submit the requested explanation |
| POST | `/fraud-cases/{case_id}/decision` | Record a human final decision |

The `fraud_type` filter matches **any contributing category**, including a secondary category.
`fraud_type` in the case response is its primary category; `fraud_types` lists them all.

For a case in `detected`, submit the following bodies in order using Swagger UI:

1. `POST /fraud-cases/{case_id}/review`

   ```json
   {"reviewer":"control_user_01","reason":"Inspecting the GPS source records."}
   ```

2. `POST /fraud-cases/{case_id}/request-explanation`

   ```json
   {"reviewer":"control_user_01","reason":"Please explain the recorded location jump."}
   ```

3. `POST /fraud-cases/{case_id}/explanation`

   ```json
   {"explanation":"The GPS signal became unstable while travelling through a tunnel."}
   ```

4. `POST /fraud-cases/{case_id}/decision`

   ```json
   {"decision":"dismissed","reviewer":"control_user_01","reason":"Signal loss was verified against the source records."}
   ```

Decisions are `dismissed` or `confirmed_fraud`. A reviewer may also decide directly from
`under_review` when an explanation is unnecessary. Once an explanation has been requested, the
workflow requires a response before deciding; there is no timeout/override mechanism in this milestone.
Invalid transitions return HTTP 409, missing records 404, and invalid request bodies/filters 422.
Terminal cases cannot be reopened. Confirming fraud changes the **case**, never the driver's status.

This is a local prototype: authentication and authorization are not implemented. Reviewer names and
driver explanations are supplied by the caller, not verified identities. Compose exposes services
only on loopback. Add authenticated roles and ownership checks before shared or production access.

## Configure rules and scoring

Defaults live in `backend/app/core/config.py`. Set `FRAUD_RULES` to a JSON object in `.env` to override
thresholds. To change weights, provide all four categories:

```dotenv
FRAUD_RULES={"gps_max_speed_kmh":200,"weights":{"gps_spoofing":35,"repeated_trips":25,"shared_device":25,"promotion_abuse":15}}
```

Recreate the Compose backend after changing its environment: `docker compose up -d backend`.
Each category contributes once; the total is capped at 100. Individual evidence `score` fields
show their category's weight and must not be summed across repeated signals. `score_breakdown`
contains the actual category contributions before the overall cap.

Cases retain their rule settings and evidence snapshot. Identical sources and settings produce
the same detection fingerprint; changing detected evidence or settings can create a new investigation
snapshot. Earlier cases, explanations, and final decisions remain intact. There is no automatic
case merging or incremental ingestion in this milestone.

## Migrations

Run on the host after installing dependencies, or prefix each command with
`docker compose exec backend`:

```bash
alembic -c backend/alembic.ini current
alembic -c backend/alembic.ini upgrade head
alembic -c backend/alembic.ini revision --autogenerate -m "describe schema change"
alembic -c backend/alembic.ini downgrade -1
```

Review autogenerated migrations before applying them, particularly enum check constraints.
The initial migration is self-contained DDL; it does not import live application models.
Rolling back the initial migration drops the application tables and their data. Use rollback on
a disposable development database or after taking an appropriate backup.

## Tests

```bash
python -m pytest -q
python -m ruff check backend scripts
python -m ruff format --check backend scripts
# Or, inside the running backend:
docker compose exec backend python -m pytest -q
```

Small deterministic fixtures test each detector, scoring, database constraints, source traceability,
transaction rollback, all status transitions, API validation, and migration upgrade/downgrade.
One end-to-end test also verifies the full 5,000-trip dataset. SQLite is used only for lightweight
tests; the application database is PostgreSQL.

The PostgreSQL tests additionally check JSONB, schema/model agreement, sequences after import,
concurrent detection deduplication, competing final decisions, and the complete review flow.
Create a **dedicated test database**, then set `TEST_DATABASE_URL`:

```bash
docker compose exec db createdb -U fraud fraud_investigation_test
```

On Linux/macOS:

```bash
export TEST_DATABASE_URL=postgresql+psycopg://fraud:local-development-change-me@localhost:5432/fraud_investigation_test
python -m pytest -q
```

On PowerShell:

```powershell
$env:TEST_DATABASE_URL = 'postgresql+psycopg://fraud:local-development-change-me@localhost:5432/fraud_investigation_test'
python -m pytest -q
```

Adjust the example credentials to your local `.env`. Each PostgreSQL test creates and removes its
own randomly named schema. Without `TEST_DATABASE_URL`, these tests are explicitly skipped.
The included GitHub Actions workflow supplies PostgreSQL and runs them on every push/PR.

## Development boundaries

No frontend, uploads, external payment integration, production deployment, model training, or
driver punishment is included. GPS tracks are plausible interpolated synthetic paths, not road-network
simulations. Rule thresholds are examples requiring calibration and review against real data.
Structured application logs use UTC timestamps and avoid logging explanation text or credentials.
Database storage uses timezone-aware timestamps; monetary values use fixed precision decimals.
