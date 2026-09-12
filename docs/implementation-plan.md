# Milestone 1 implementation contract

## Plan

1. Define SQLAlchemy entities, UTC timestamps, constraints, and an explicit Alembic migration.
2. Implement pure structured detectors and centralized, configurable category scoring.
3. Generate deterministic normal data and injected, source-linked ground truth.
4. Persist immutable case snapshots and evidence in a single transaction; make reruns idempotent.
5. Expose read APIs and transactional human review, explanation, and decision workflows.
6. Verify rules, persistence, migrations, API transitions, and the full synthetic scenario flow.
7. Document Docker/local setup, rule limitations, and evidence inspection.

## Domain and schema decisions

- Drivers own trips; GPS events reference both trip and driver with a composite foreign key.
- Driver-device associations record observed first/last use; sharing is an anomaly, not proof of fraud.
- Promotions contain a validity period, trip threshold, and reward; trips optionally reference them.
- One case is an aggregate investigation for a driver and a detected source snapshot. `fraud_type` is
  the primary (highest weighted) category; `fraud_types` retains all contributing categories.
- A case keeps its overall score, category contributions, rule configuration, and detection fingerprint.
- Evidence keeps a structured signal, numeric measurements, and relational links to all original
  trips, GPS events, devices, drivers, and promotions used by the rule.
- Explanations and decisions are append-only. Attachment metadata is reserved as JSON, without uploads.
- Status uses portable string enums plus database checks, changed by future migrations rather than
  PostgreSQL native enum alteration. Terminal decisions cannot be reopened through this API.
- Automated detection never changes driver status or makes a final case decision.

## Rule interface

Each detector accepts a typed driver observation (trips, GPS, device memberships, promotions) and
validated rule settings, returning `list[Signal]`. A signal has a category, rule name, severity,
description, source type/id, typed source references, and JSON-safe measurable details. Detectors
perform no database writes. Scoring assigns each category's weight once and caps the sum at 100;
every signal remains visible even when its category contributes only once.

## Acceptance criteria

- Docker Compose defines only PostgreSQL and the backend; Alembic creates and rolls back the schema.
- Seed 42 produces 100 drivers, 5,000 trips, plausible GPS tracks, devices, and promotions reproducibly.
- D001 has impossible GPS movement, D014 repeated short routes, D027 shared device usage with D028
  and D029, and D050 promotion abuse (also repeated trips). Ground truth identifies source records.
- Detection creates explainable, traceable cases; identical reruns create no duplicates and never
  reset review outcomes. Independent new source evidence may create a new case.
- API supports paginated drivers/cases, category/status/score/driver filters, original evidence
  sources, review transitions, explanations, and explicit human decisions with a reason.
- Small deterministic tests cover every detector, scoring, case/evidence persistence, integrity,
  valid/invalid transitions, and API behavior. PostgreSQL integration tests exercise migrations
  and the complete flow when a dedicated test database is supplied.
