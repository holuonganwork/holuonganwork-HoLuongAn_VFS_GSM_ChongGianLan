"""Initial investigation schema. Frozen DDL independent of live application models."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "devices",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("device_identifier", sa.String(length=200), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_devices")),
        sa.UniqueConstraint("device_identifier", name=op.f("uq_devices_device_identifier")),
    )
    op.create_table(
        "drivers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("external_driver_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_drivers")),
        sa.UniqueConstraint("external_driver_id", name=op.f("uq_drivers_external_driver_id")),
    )
    op.create_table(
        "promotions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("trip_threshold", sa.Integer(), nullable=False),
        sa.Column("reward_amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("ends_at > starts_at", name=op.f("ck_promotions_valid_period")),
        sa.CheckConstraint(
            "trip_threshold > 0 AND reward_amount >= 0", name=op.f("ck_promotions_valid_reward")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_promotions")),
        sa.UniqueConstraint("code", name=op.f("uq_promotions_code")),
    )
    op.create_table(
        "driver_devices",
        sa.Column("driver_id", sa.Integer(), nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "last_seen_at >= first_seen_at", name=op.f("ck_driver_devices_valid_period")
        ),
        sa.ForeignKeyConstraint(
            ["device_id"], ["devices.id"], name=op.f("fk_driver_devices_device_id_devices")
        ),
        sa.ForeignKeyConstraint(
            ["driver_id"], ["drivers.id"], name=op.f("fk_driver_devices_driver_id_drivers")
        ),
        sa.PrimaryKeyConstraint("driver_id", "device_id", name=op.f("pk_driver_devices")),
    )
    op.create_index("ix_driver_devices_device_id", "driver_devices", ["device_id"], unique=False)
    op.create_table(
        "fraud_cases",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("driver_id", sa.Integer(), nullable=False),
        sa.Column(
            "fraud_type",
            sa.Enum(
                "gps_spoofing",
                "repeated_trips",
                "shared_device",
                "promotion_abuse",
                name="fraud_type",
                native_enum=False,
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column(
            "fraud_types",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=False,
        ),
        sa.Column("risk_score", sa.Integer(), nullable=False),
        sa.Column(
            "score_breakdown",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=False,
        ),
        sa.Column(
            "rule_config",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=False,
        ),
        sa.Column("detection_fingerprint", sa.String(length=64), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "detected",
                "under_review",
                "awaiting_driver_explanation",
                "driver_responded",
                "confirmed_fraud",
                "dismissed",
                name="case_status",
                native_enum=False,
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "risk_score BETWEEN 0 AND 100", name=op.f("ck_fraud_cases_valid_risk_score")
        ),
        sa.ForeignKeyConstraint(
            ["driver_id"], ["drivers.id"], name=op.f("fk_fraud_cases_driver_id_drivers")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_fraud_cases")),
        sa.UniqueConstraint(
            "detection_fingerprint", name=op.f("uq_fraud_cases_detection_fingerprint")
        ),
    )
    op.create_index(op.f("ix_fraud_cases_driver_id"), "fraud_cases", ["driver_id"], unique=False)
    op.create_index(op.f("ix_fraud_cases_fraud_type"), "fraud_cases", ["fraud_type"], unique=False)
    op.create_index(
        "ix_fraud_cases_status_risk", "fraud_cases", ["status", "risk_score"], unique=False
    )
    op.create_table(
        "trips",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("driver_id", sa.Integer(), nullable=False),
        sa.Column("pickup_lat", sa.Float(), nullable=False),
        sa.Column("pickup_lng", sa.Float(), nullable=False),
        sa.Column("dropoff_lat", sa.Float(), nullable=False),
        sa.Column("dropoff_lng", sa.Float(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("distance_km", sa.Float(), nullable=False),
        sa.Column("fare_amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("promotion_amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("promotion_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "distance_km >= 0 AND fare_amount >= 0 AND promotion_amount >= 0",
            name=op.f("ck_trips_nonnegative_amounts"),
        ),
        sa.CheckConstraint("ended_at > started_at", name=op.f("ck_trips_valid_period")),
        sa.CheckConstraint(
            "pickup_lat BETWEEN -90 AND 90 AND dropoff_lat BETWEEN -90 AND 90",
            name=op.f("ck_trips_valid_latitudes"),
        ),
        sa.CheckConstraint(
            "pickup_lng BETWEEN -180 AND 180 AND dropoff_lng BETWEEN -180 AND 180",
            name=op.f("ck_trips_valid_longitudes"),
        ),
        sa.ForeignKeyConstraint(
            ["driver_id"], ["drivers.id"], name=op.f("fk_trips_driver_id_drivers")
        ),
        sa.ForeignKeyConstraint(
            ["promotion_id"], ["promotions.id"], name=op.f("fk_trips_promotion_id_promotions")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_trips")),
        sa.UniqueConstraint("id", "driver_id", name=op.f("uq_trips_id")),
    )
    op.create_index("ix_trips_driver_started", "trips", ["driver_id", "started_at"], unique=False)
    op.create_index(op.f("ix_trips_promotion_id"), "trips", ["promotion_id"], unique=False)
    op.create_table(
        "case_decisions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("case_id", sa.Integer(), nullable=False),
        sa.Column(
            "decision",
            sa.Enum(
                "detected",
                "under_review",
                "awaiting_driver_explanation",
                "driver_responded",
                "confirmed_fraud",
                "dismissed",
                name="decision",
                native_enum=False,
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column("reviewer", sa.String(length=200), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "decision IN ('confirmed_fraud', 'dismissed')",
            name=op.f("ck_case_decisions_terminal_decision"),
        ),
        sa.ForeignKeyConstraint(
            ["case_id"], ["fraud_cases.id"], name=op.f("fk_case_decisions_case_id_fraud_cases")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_case_decisions")),
        sa.UniqueConstraint("case_id", name=op.f("uq_case_decisions_case_id")),
    )
    op.create_table(
        "case_status_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("case_id", sa.Integer(), nullable=False),
        sa.Column(
            "from_status",
            sa.Enum(
                "detected",
                "under_review",
                "awaiting_driver_explanation",
                "driver_responded",
                "confirmed_fraud",
                "dismissed",
                name="from_status",
                native_enum=False,
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column(
            "to_status",
            sa.Enum(
                "detected",
                "under_review",
                "awaiting_driver_explanation",
                "driver_responded",
                "confirmed_fraud",
                "dismissed",
                name="to_status",
                native_enum=False,
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column("actor", sa.String(length=200), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["case_id"], ["fraud_cases.id"], name=op.f("fk_case_status_events_case_id_fraud_cases")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_case_status_events")),
    )
    op.create_index(
        op.f("ix_case_status_events_case_id"), "case_status_events", ["case_id"], unique=False
    )
    op.create_table(
        "driver_explanations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("case_id", sa.Integer(), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column(
            "attachment_metadata",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["case_id"], ["fraud_cases.id"], name=op.f("fk_driver_explanations_case_id_fraud_cases")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_driver_explanations")),
    )
    op.create_index(
        op.f("ix_driver_explanations_case_id"), "driver_explanations", ["case_id"], unique=False
    )
    op.create_table(
        "fraud_evidences",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("case_id", sa.Integer(), nullable=False),
        sa.Column(
            "fraud_type",
            sa.Enum(
                "gps_spoofing",
                "repeated_trips",
                "shared_device",
                "promotion_abuse",
                name="fraud_type",
                native_enum=False,
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column("evidence_type", sa.String(length=100), nullable=False),
        sa.Column(
            "source_type",
            sa.Enum(
                "driver",
                "trip",
                "gps_event",
                "device",
                "promotion",
                name="source_type",
                native_enum=False,
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column(
            "severity",
            sa.Enum("medium", "high", name="severity", native_enum=False, create_constraint=True),
            nullable=False,
        ),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "evidence_data",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("score BETWEEN 0 AND 100", name=op.f("ck_fraud_evidences_valid_score")),
        sa.ForeignKeyConstraint(
            ["case_id"], ["fraud_cases.id"], name=op.f("fk_fraud_evidences_case_id_fraud_cases")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_fraud_evidences")),
    )
    op.create_index(
        op.f("ix_fraud_evidences_case_id"), "fraud_evidences", ["case_id"], unique=False
    )
    op.create_index(
        op.f("ix_fraud_evidences_fraud_type"), "fraud_evidences", ["fraud_type"], unique=False
    )
    op.create_table(
        "gps_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("driver_id", sa.Integer(), nullable=False),
        sa.Column("trip_id", sa.Integer(), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "latitude BETWEEN -90 AND 90", name=op.f("ck_gps_events_valid_latitude")
        ),
        sa.CheckConstraint(
            "longitude BETWEEN -180 AND 180", name=op.f("ck_gps_events_valid_longitude")
        ),
        sa.ForeignKeyConstraint(
            ["driver_id"], ["drivers.id"], name=op.f("fk_gps_events_driver_id_drivers")
        ),
        sa.ForeignKeyConstraint(
            ["trip_id", "driver_id"],
            ["trips.id", "trips.driver_id"],
            name=op.f("fk_gps_events_trip_id_trips"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_gps_events")),
    )
    op.create_index(
        "ix_gps_events_driver_recorded", "gps_events", ["driver_id", "recorded_at"], unique=False
    )
    op.create_index(
        "ix_gps_events_trip_recorded", "gps_events", ["trip_id", "recorded_at"], unique=False
    )
    op.create_table(
        "evidence_sources",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("evidence_id", sa.Integer(), nullable=False),
        sa.Column(
            "source_type",
            sa.Enum(
                "driver",
                "trip",
                "gps_event",
                "device",
                "promotion",
                name="source_type",
                native_enum=False,
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("driver_id", sa.Integer(), nullable=True),
        sa.Column("trip_id", sa.Integer(), nullable=True),
        sa.Column("gps_event_id", sa.Integer(), nullable=True),
        sa.Column("device_id", sa.Integer(), nullable=True),
        sa.Column("promotion_id", sa.Integer(), nullable=True),
        sa.CheckConstraint(
            "(source_type = 'driver' AND driver_id IS NOT NULL AND source_id = driver_id) OR "
            "(source_type = 'trip' AND trip_id IS NOT NULL AND source_id = trip_id) OR "
            "(source_type = 'gps_event' AND gps_event_id IS NOT NULL "
            "AND source_id = gps_event_id) OR "
            "(source_type = 'device' AND device_id IS NOT NULL AND source_id = device_id) OR "
            "(source_type = 'promotion' AND promotion_id IS NOT NULL AND source_id = promotion_id)",
            name=op.f("ck_evidence_sources_source_matches"),
        ),
        sa.CheckConstraint(
            "(CASE WHEN driver_id IS NULL THEN 0 ELSE 1 END + "
            "CASE WHEN trip_id IS NULL THEN 0 ELSE 1 END + "
            "CASE WHEN gps_event_id IS NULL THEN 0 ELSE 1 END + "
            "CASE WHEN device_id IS NULL THEN 0 ELSE 1 END + "
            "CASE WHEN promotion_id IS NULL THEN 0 ELSE 1 END) = 1",
            name=op.f("ck_evidence_sources_one_source"),
        ),
        sa.ForeignKeyConstraint(
            ["device_id"], ["devices.id"], name=op.f("fk_evidence_sources_device_id_devices")
        ),
        sa.ForeignKeyConstraint(
            ["driver_id"], ["drivers.id"], name=op.f("fk_evidence_sources_driver_id_drivers")
        ),
        sa.ForeignKeyConstraint(
            ["evidence_id"],
            ["fraud_evidences.id"],
            name=op.f("fk_evidence_sources_evidence_id_fraud_evidences"),
        ),
        sa.ForeignKeyConstraint(
            ["gps_event_id"],
            ["gps_events.id"],
            name=op.f("fk_evidence_sources_gps_event_id_gps_events"),
        ),
        sa.ForeignKeyConstraint(
            ["promotion_id"],
            ["promotions.id"],
            name=op.f("fk_evidence_sources_promotion_id_promotions"),
        ),
        sa.ForeignKeyConstraint(
            ["trip_id"], ["trips.id"], name=op.f("fk_evidence_sources_trip_id_trips")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_evidence_sources")),
        sa.UniqueConstraint(
            "evidence_id", "source_type", "source_id", name=op.f("uq_evidence_sources_evidence_id")
        ),
    )
    op.create_index(
        op.f("ix_evidence_sources_device_id"), "evidence_sources", ["device_id"], unique=False
    )
    op.create_index(
        op.f("ix_evidence_sources_driver_id"), "evidence_sources", ["driver_id"], unique=False
    )
    op.create_index(
        op.f("ix_evidence_sources_evidence_id"), "evidence_sources", ["evidence_id"], unique=False
    )
    op.create_index(
        op.f("ix_evidence_sources_gps_event_id"), "evidence_sources", ["gps_event_id"], unique=False
    )
    op.create_index(
        op.f("ix_evidence_sources_promotion_id"), "evidence_sources", ["promotion_id"], unique=False
    )
    op.create_index(
        op.f("ix_evidence_sources_trip_id"), "evidence_sources", ["trip_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_evidence_sources_trip_id"), table_name="evidence_sources")
    op.drop_index(op.f("ix_evidence_sources_promotion_id"), table_name="evidence_sources")
    op.drop_index(op.f("ix_evidence_sources_gps_event_id"), table_name="evidence_sources")
    op.drop_index(op.f("ix_evidence_sources_evidence_id"), table_name="evidence_sources")
    op.drop_index(op.f("ix_evidence_sources_driver_id"), table_name="evidence_sources")
    op.drop_index(op.f("ix_evidence_sources_device_id"), table_name="evidence_sources")
    op.drop_table("evidence_sources")
    op.drop_index("ix_gps_events_trip_recorded", table_name="gps_events")
    op.drop_index("ix_gps_events_driver_recorded", table_name="gps_events")
    op.drop_table("gps_events")
    op.drop_index(op.f("ix_fraud_evidences_fraud_type"), table_name="fraud_evidences")
    op.drop_index(op.f("ix_fraud_evidences_case_id"), table_name="fraud_evidences")
    op.drop_table("fraud_evidences")
    op.drop_index(op.f("ix_driver_explanations_case_id"), table_name="driver_explanations")
    op.drop_table("driver_explanations")
    op.drop_index(op.f("ix_case_status_events_case_id"), table_name="case_status_events")
    op.drop_table("case_status_events")
    op.drop_table("case_decisions")
    op.drop_index(op.f("ix_trips_promotion_id"), table_name="trips")
    op.drop_index("ix_trips_driver_started", table_name="trips")
    op.drop_table("trips")
    op.drop_index("ix_fraud_cases_status_risk", table_name="fraud_cases")
    op.drop_index(op.f("ix_fraud_cases_fraud_type"), table_name="fraud_cases")
    op.drop_index(op.f("ix_fraud_cases_driver_id"), table_name="fraud_cases")
    op.drop_table("fraud_cases")
    op.drop_index("ix_driver_devices_device_id", table_name="driver_devices")
    op.drop_table("driver_devices")
    op.drop_table("promotions")
    op.drop_table("drivers")
    op.drop_table("devices")
