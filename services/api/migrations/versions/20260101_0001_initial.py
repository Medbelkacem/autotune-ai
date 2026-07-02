"""initial schema

Revision ID: 20260101_0001
Revises:
Create Date: 2026-01-01 00:00:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20260101_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")
    op.execute("CREATE EXTENSION IF NOT EXISTS \"pgcrypto\"")
    op.execute("CREATE EXTENSION IF NOT EXISTS citext")
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    # organization
    op.create_table(
        "organization",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("plan", sa.String(32), nullable=False, server_default="free"),
        sa.Column("region", sa.String(8), nullable=False, server_default="US"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("plan IN ('free','pro','workshop','enterprise','oem','gov')",
                           name="organization_plan_check"),
    )

    op.create_table(
        "subscription",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("organization.id", ondelete="CASCADE"), nullable=False),
        sa.Column("stripe_subscription_id", sa.Text),
        sa.Column("plan", sa.String(32), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="active"),
        sa.Column("seats", sa.Integer, nullable=False, server_default="1"),
        sa.Column("current_period_end", sa.DateTime(timezone=True)),
        sa.Column("meta", postgresql.JSONB, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_subscription_org_id", "subscription", ["org_id"])

    # users
    op.create_table(
        "app_user",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("organization.id", ondelete="CASCADE"), nullable=False),
        sa.Column("email", postgresql.CITEXT, nullable=False),
        sa.Column("name", sa.Text),
        sa.Column("pwd_hash", sa.Text),
        sa.Column("mfa_secret", sa.LargeBinary),
        sa.Column("totp_enrolled", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("webauthn", postgresql.JSONB, server_default="{}"),
        sa.Column("status", sa.String(16), server_default="active"),
        sa.Column("last_login_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("email", name="uq_user_email"),
    )
    op.create_index("ix_app_user_org_id", "app_user", ["org_id"])

    # rbac
    op.create_table(
        "role",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.Text, nullable=False, unique=True),
    )
    op.create_table(
        "permission",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("code", sa.Text, nullable=False, unique=True),
        sa.Column("description", sa.Text),
    )
    op.create_table(
        "role_permission",
        sa.Column("role_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("role.id", ondelete="CASCADE")),
        sa.Column("permission_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("permission.id", ondelete="CASCADE")),
        sa.PrimaryKeyConstraint("role_id", "permission_id"),
    )
    op.create_table(
        "role_assignment",
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("app_user.id", ondelete="CASCADE")),
        sa.Column("role_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("role.id", ondelete="CASCADE")),
        sa.Column("scope", sa.Text, nullable=False, server_default="org"),
        sa.PrimaryKeyConstraint("user_id", "role_id", "scope"),
    )

    # api keys, sessions
    op.create_table(
        "api_key",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("app_user.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("key_prefix", sa.String(12), nullable=False, index=True),
        sa.Column("key_hash", sa.Text, nullable=False),
        sa.Column("last_used_at", sa.DateTime(timezone=True)),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "user_session",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("app_user.id", ondelete="CASCADE"), nullable=False),
        sa.Column("refresh_token_jti", sa.String(64), nullable=False, unique=True),
        sa.Column("user_agent", sa.Text),
        sa.Column("ip", sa.String(64)),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # vehicles + ecu
    op.create_table(
        "vehicle",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("organization.id", ondelete="CASCADE"), nullable=False),
        sa.Column("vin", sa.Text, nullable=False),
        sa.Column("manufacturer", sa.Text),
        sa.Column("model", sa.Text),
        sa.Column("year", sa.Integer),
        sa.Column("engine_code", sa.Text),
        sa.Column("transmission_code", sa.Text),
        sa.Column("fuel_type", sa.Text),
        sa.Column("emission_standard", sa.Text),
        sa.Column("modification", postgresql.JSONB, server_default="{}"),
        sa.Column("signed_identity", sa.LargeBinary),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("org_id", "vin", name="uq_vehicle_vin_org"),
    )
    op.create_index("ix_vehicle_org_id", "vehicle", ["org_id"])

    op.create_table(
        "ecu_profile",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("vehicle_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("vehicle.id", ondelete="CASCADE"), nullable=False),
        sa.Column("vendor", sa.Text),
        sa.Column("model", sa.Text),
        sa.Column("hardware_pn", sa.Text),
        sa.Column("software_pn", sa.Text),
        sa.Column("calibration_pn", sa.Text),
        sa.Column("firmware_sha256", sa.LargeBinary, nullable=False),
        sa.Column("protocols", postgresql.ARRAY(sa.Text)),
        sa.Column("detected_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_ecu_profile_vehicle_id", "ecu_profile", ["vehicle_id"])
    op.create_index("ix_ecu_profile_firmware_sha256", "ecu_profile", ["firmware_sha256"])

    # calibration document + maps
    op.create_table(
        "calibration_document",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("ecu_profile_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("ecu_profile.id", ondelete="CASCADE"), nullable=False),
        sa.Column("a2l_version", sa.Text),
        sa.Column("page_checksums", postgresql.JSONB, server_default="{}"),
        sa.Column("provenance", postgresql.JSONB, server_default="{}"),
        sa.Column("s3_uri", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_calibration_document_ecu_profile_id",
                    "calibration_document", ["ecu_profile_id"])

    op.create_table(
        "map_record",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("document_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("calibration_document.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("address_hex", sa.Text, nullable=False),
        sa.Column("datatype", sa.Text, nullable=False),
        sa.Column("unit", sa.Text),
        sa.Column("phys_min", sa.Numeric),
        sa.Column("phys_max", sa.Numeric),
        sa.Column("rows", sa.Integer, server_default="1"),
        sa.Column("cols", sa.Integer, server_default="1"),
        sa.Column("values", postgresql.JSONB, nullable=False),
        sa.Column("axes", postgresql.JSONB, server_default="{}"),
        sa.Column("description", sa.Text),
        sa.Column("page_hash_sha256", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_map_record_document_id", "map_record", ["document_id"])
    op.create_index("ix_map_record_name", "map_record", ["name"])

    # scan session + report + recommendation
    op.create_table(
        "scan_session",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("vehicle_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("vehicle.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("app_user.id", ondelete="SET NULL")),
        sa.Column("bridge_id", sa.Text),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("ended_at", sa.DateTime(timezone=True)),
        sa.Column("status", sa.Text, nullable=False, server_default="running"),
        sa.Column("details", postgresql.JSONB, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_scan_session_vehicle_id", "scan_session", ["vehicle_id"])

    op.create_table(
        "analysis_report",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("scan_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("scan_session.id", ondelete="CASCADE"), nullable=False),
        sa.Column("profile", sa.Text, nullable=False),
        sa.Column("cards", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("health_score", sa.Integer),
        sa.Column("summary", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_analysis_report_scan_id", "analysis_report", ["scan_id"])

    op.create_table(
        "recommendation",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("report_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("analysis_report.id", ondelete="CASCADE"), nullable=False),
        sa.Column("safety_score", sa.Integer, nullable=False),
        sa.Column("confidence_score", sa.Numeric(4, 3), nullable=False),
        sa.Column("compat_score", sa.Integer, nullable=False),
        sa.Column("predicted_gains", postgresql.JSONB, server_default="{}"),
        sa.Column("bundle", postgresql.JSONB, nullable=False),
        sa.Column("approved_by", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("app_user.id", ondelete="SET NULL")),
        sa.Column("signed_blob", sa.LargeBinary),
        sa.Column("status", sa.Text, nullable=False, server_default="simulation"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_recommendation_report_id", "recommendation", ["report_id"])
    op.create_index(
        "ix_recommendation_pending_review",
        "recommendation",
        ["created_at"],
        postgresql_where=sa.text("status = 'pending_review'"),
    )

    # telemetry
    op.create_table(
        "telemetry_stream",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("vehicle_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("vehicle.id", ondelete="CASCADE"), nullable=False),
        sa.Column("bridge_id", sa.Text),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("ended_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_telemetry_stream_vehicle_id", "telemetry_stream", ["vehicle_id"])

    op.create_table(
        "health_event",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("stream_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("telemetry_stream.id", ondelete="CASCADE"), nullable=False),
        sa.Column("severity", sa.Text, nullable=False),
        sa.Column("channel", sa.Text, nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("value", sa.Numeric),
        sa.Column("threshold", sa.Numeric),
        sa.Column("meta", postgresql.JSONB, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_health_event_stream_id", "health_event", ["stream_id"])

    # KB + embeddings
    op.create_table(
        "kb_doc",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("source", sa.Text, nullable=False),
        sa.Column("uri", sa.Text),
        sa.Column("sha256", sa.Text, nullable=False, unique=True),
        sa.Column("meta", postgresql.JSONB, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "kb_chunk",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("doc_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("kb_doc.id", ondelete="CASCADE"), nullable=False),
        sa.Column("ord", sa.Integer, nullable=False),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("locator", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_kb_chunk_doc_id", "kb_chunk", ["doc_id"])

    op.execute("""
        CREATE TABLE embedding (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            chunk_id UUID NOT NULL REFERENCES kb_chunk(id) ON DELETE CASCADE,
            model TEXT NOT NULL,
            vec vector(1024) NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        CREATE INDEX ix_embedding_chunk_id ON embedding(chunk_id);
        CREATE INDEX ix_embedding_vec ON embedding USING hnsw (vec vector_cosine_ops);
    """)

    # audit
    op.create_table(
        "audit_log",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("actor", postgresql.UUID(as_uuid=True)),
        sa.Column("action", sa.Text, nullable=False),
        sa.Column("target", sa.Text, nullable=False),
        sa.Column("payload", postgresql.JSONB, server_default="{}"),
        sa.Column("hash_prev", sa.LargeBinary),
        sa.Column("hash_self", sa.LargeBinary, nullable=False),
    )
    op.create_index("ix_audit_log_ts", "audit_log", ["ts"])
    op.create_index("ix_audit_log_actor", "audit_log", ["actor"])

    # bridge
    op.create_table(
        "bridge",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("organization.id", ondelete="CASCADE"), nullable=False),
        sa.Column("serial", sa.Text, nullable=False, unique=True),
        sa.Column("model", sa.Text, nullable=False),
        sa.Column("firmware_version", sa.Text),
        sa.Column("public_key_b64", sa.Text, nullable=False),
        sa.Column("attested", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("last_seen_at", sa.DateTime(timezone=True)),
        sa.Column("meta", postgresql.JSONB, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_bridge_org_id", "bridge", ["org_id"])


def downgrade() -> None:
    for t in [
        "bridge",
        "audit_log",
        "embedding",
        "kb_chunk",
        "kb_doc",
        "health_event",
        "telemetry_stream",
        "recommendation",
        "analysis_report",
        "scan_session",
        "map_record",
        "calibration_document",
        "ecu_profile",
        "vehicle",
        "user_session",
        "api_key",
        "role_assignment",
        "role_permission",
        "permission",
        "role",
        "app_user",
        "subscription",
        "organization",
    ]:
        op.execute(f"DROP TABLE IF EXISTS {t} CASCADE")
