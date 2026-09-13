"""Add correlated alerts and policy decisions without rewriting historical cases."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0002_alert_decisions"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "fraud_alerts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("driver_id", sa.Integer(), nullable=False),
        sa.Column("correlation_key", sa.String(length=64), nullable=False),
        sa.Column("detection_fingerprint", sa.String(length=64), nullable=False),
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
            "fraud_types", sa.JSON().with_variant(postgresql.JSONB(), "postgresql"), nullable=False
        ),
        sa.Column(
            "severity",
            sa.Enum("medium", "high", name="severity", native_enum=False, create_constraint=True),
            nullable=False,
        ),
        sa.Column("risk_score", sa.Integer(), nullable=False),
        sa.Column("fraud_probability", sa.Float(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column(
            "impact",
            sa.Enum(
                "unknown",
                "low",
                "high",
                "critical",
                name="impact",
                native_enum=False,
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column("model_version", sa.String(length=100), nullable=False),
        sa.Column(
            "assessment", sa.JSON().with_variant(postgresql.JSONB(), "postgresql"), nullable=False
        ),
        sa.Column(
            "rule_config", sa.JSON().with_variant(postgresql.JSONB(), "postgresql"), nullable=False
        ),
        sa.Column(
            "signals", sa.JSON().with_variant(postgresql.JSONB(), "postgresql"), nullable=False
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "confidence BETWEEN 0 AND 1", name=op.f("ck_fraud_alerts_valid_confidence")
        ),
        sa.CheckConstraint(
            "fraud_probability BETWEEN 0 AND 1", name=op.f("ck_fraud_alerts_valid_probability")
        ),
        sa.CheckConstraint(
            "risk_score BETWEEN 0 AND 100", name=op.f("ck_fraud_alerts_valid_risk_score")
        ),
        sa.ForeignKeyConstraint(
            ["driver_id"], ["drivers.id"], name=op.f("fk_fraud_alerts_driver_id_drivers")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_fraud_alerts")),
        sa.UniqueConstraint(
            "detection_fingerprint", name=op.f("uq_fraud_alerts_detection_fingerprint")
        ),
    )
    with op.batch_alter_table("fraud_alerts", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_fraud_alerts_correlation_key"), ["correlation_key"], unique=False
        )
        batch_op.create_index(batch_op.f("ix_fraud_alerts_driver_id"), ["driver_id"], unique=False)

    op.create_table(
        "decision_results",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("alert_id", sa.Integer(), nullable=False),
        sa.Column(
            "outcome",
            sa.Enum(
                "auto_clear",
                "auto_fraud",
                "human_review",
                name="decision_outcome",
                native_enum=False,
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("policy_version", sa.String(length=100), nullable=False),
        sa.Column(
            "policy_config",
            sa.JSON().with_variant(postgresql.JSONB(), "postgresql"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["alert_id"],
            ["fraud_alerts.id"],
            name=op.f("fk_decision_results_alert_id_fraud_alerts"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_decision_results")),
        sa.UniqueConstraint("alert_id", name=op.f("uq_decision_results_alert_id")),
    )
    with op.batch_alter_table("decision_results", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_decision_results_outcome"), ["outcome"], unique=False)

    with op.batch_alter_table("case_decisions", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "actor_type",
                sa.Enum(
                    "human",
                    "system",
                    name="decision_actor",
                    native_enum=False,
                    create_constraint=True,
                ),
                server_default="human",
                nullable=False,
            )
        )

    with op.batch_alter_table("fraud_cases", schema=None) as batch_op:
        batch_op.add_column(sa.Column("alert_id", sa.Integer(), nullable=True))
        batch_op.create_unique_constraint(batch_op.f("uq_fraud_cases_alert_id"), ["alert_id"])
        batch_op.create_foreign_key(
            batch_op.f("fk_fraud_cases_alert_id_fraud_alerts"), "fraud_alerts", ["alert_id"], ["id"]
        )


def downgrade() -> None:
    with op.batch_alter_table("fraud_cases", schema=None) as batch_op:
        batch_op.drop_constraint(
            batch_op.f("fk_fraud_cases_alert_id_fraud_alerts"), type_="foreignkey"
        )
        batch_op.drop_constraint(batch_op.f("uq_fraud_cases_alert_id"), type_="unique")
        batch_op.drop_column("alert_id")

    with op.batch_alter_table("case_decisions", schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f("ck_case_decisions_decision_actor"), type_="check")
        batch_op.drop_column("actor_type")

    with op.batch_alter_table("decision_results", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_decision_results_outcome"))

    op.drop_table("decision_results")
    with op.batch_alter_table("fraud_alerts", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_fraud_alerts_driver_id"))
        batch_op.drop_index(batch_op.f("ix_fraud_alerts_correlation_key"))

    op.drop_table("fraud_alerts")
