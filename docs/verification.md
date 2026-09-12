# Milestone 1 verification

Verified locally on 2026-09-12 with Python 3.11, PostgreSQL 16, and Docker Compose.

| Check | Observed result |
| --- | --- |
| Compose build/start | PostgreSQL and backend containers healthy; both ports bound to loopback |
| Initial migration | Applied to PostgreSQL successfully |
| Schema agreement | `alembic check`: no new upgrade operations detected |
| Automated suite with PostgreSQL enabled | 81 passed, zero skipped; two upstream test-client deprecation warnings |
| Migration round trip | Upgrade, downgrade, model comparison, and self-contained autogeneration passed |
| Ruff checks | Lint and formatting passed |
| Seed 42 import | 100 drivers, 5,000 trips, 30,000 GPS events, 101 devices, 103 associations, one promotion |
| Detection | Six cases and eight evidence records; categories match injected ground truth |
| Identical rerun | Zero new cases/evidence, six existing cases reused |
| Concurrent PostgreSQL operations | Duplicate detection and competing final decisions serialized correctly |
| Review workflow | Explanation and final decision tested through FastAPI against PostgreSQL |
| Running HTTP service | Health, driver/case/evidence reads, Swagger UI, and OpenAPI returned successfully |
| Original evidence sources | All 55 references across eight evidence items resolved to original records |
| Driver status | All 100 local synthetic drivers remain active |

Dataset SHA-256:
`42ed129f7486fdc2ef7a4896de1304265a3e8becdfdca7e11e39906a5bb4164c`.

Generated local artifacts (intentionally ignored by Git): `data/generated/dataset.json`,
`manifest.json`, and `api-example.json` containing the GPS investigation response.
The local development cases remain in `detected`; review tests used isolated test schemas.

These checks establish behavior on the synthetic fixtures, not production accuracy, throughput,
identity verification, or deployment readiness. See the README and rule documentation for scope.
