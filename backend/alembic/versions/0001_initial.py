"""Initial schema for SecureWealth AI foundation.

Revision ID: 0001_initial
Revises: None
Create Date: 2026-07-19 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("full_name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("password_hash", sa.String(length=512), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "user_sessions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("token_id", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("token_id", name="uq_user_sessions_token_id"),
    )
    op.create_index("ix_user_sessions_user_id", "user_sessions", ["user_id"])
    op.create_index("ix_user_sessions_token_id", "user_sessions", ["token_id"], unique=True)

    op.create_table(
        "customers",
        sa.Column("customer_id", sa.String(length=64), primary_key=True),
        sa.Column("dob", sa.Date(), nullable=True),
        sa.Column("gender", sa.String(length=16), nullable=True),
        sa.Column("location", sa.String(length=120), nullable=True),
        sa.Column("account_balance", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "transactions",
        sa.Column("transaction_id", sa.String(length=64), primary_key=True),
        sa.Column("customer_id", sa.String(length=64), nullable=False),
        sa.Column("transaction_date", sa.Date(), nullable=False),
        sa.Column("transaction_time", sa.Time(), nullable=False),
        sa.Column("transaction_amount", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.customer_id"], ondelete="CASCADE"),
    )
    op.create_index("ix_transactions_customer_id", "transactions", ["customer_id"])

    op.create_table(
        "behavior_profiles",
        sa.Column("customer_id", sa.String(length=64), primary_key=True),
        sa.Column("avg_transaction_amount", sa.Float(), nullable=True),
        sa.Column("transaction_frequency", sa.Float(), nullable=True),
        sa.Column("spending_pattern_json", sa.JSON(), nullable=True),
        sa.Column("risk_flags_json", sa.JSON(), nullable=True),
        sa.Column("last_updated", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.customer_id"], ondelete="CASCADE"),
    )

    op.create_table(
        "digital_wealth_twins",
        sa.Column("customer_id", sa.String(length=64), primary_key=True),
        sa.Column("financial_dna_json", sa.JSON(), nullable=True),
        sa.Column("wealth_summary", sa.Text(), nullable=True),
        sa.Column("health_score_placeholder", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.customer_id"], ondelete="CASCADE"),
    )

    op.create_table(
        "fraud_analyses",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("customer_id", sa.String(length=64), nullable=False),
        sa.Column("transaction_id", sa.String(length=64), nullable=False),
        sa.Column("fraud_score_placeholder", sa.Float(), nullable=True),
        sa.Column("anomaly_reason_placeholder", sa.Text(), nullable=True),
        sa.Column("explanation_placeholder", sa.Text(), nullable=True),
        sa.Column("evidence_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.customer_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["transaction_id"], ["transactions.transaction_id"], ondelete="CASCADE"),
    )
    op.create_index("ix_fraud_analyses_customer_id", "fraud_analyses", ["customer_id"])
    op.create_index("ix_fraud_analyses_transaction_id", "fraud_analyses", ["transaction_id"])

    op.create_table(
        "recommendations",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("customer_id", sa.String(length=64), nullable=False),
        sa.Column("recommendation_text", sa.Text(), nullable=False),
        sa.Column("priority", sa.String(length=32), nullable=False, server_default=sa.text("'medium'")),
        sa.Column("status", sa.String(length=32), nullable=False, server_default=sa.text("'active'")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.customer_id"], ondelete="CASCADE"),
    )
    op.create_index("ix_recommendations_customer_id", "recommendations", ["customer_id"])

    op.create_table(
        "agent_memories",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("customer_id", sa.String(length=64), nullable=False),
        sa.Column("conversation_memory", sa.Text(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.customer_id"], ondelete="CASCADE"),
        sa.UniqueConstraint("customer_id", name="uq_agent_memories_customer_id"),
    )
    op.create_index("ix_agent_memories_customer_id", "agent_memories", ["customer_id"], unique=True)

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_user_sessions_token_id", table_name="user_sessions")
    op.drop_index("ix_user_sessions_user_id", table_name="user_sessions")
    op.drop_table("user_sessions")
    op.drop_index("ix_audit_logs_user_id", table_name="audit_logs")
    op.drop_table("audit_logs")
    op.drop_index("ix_agent_memories_customer_id", table_name="agent_memories")
    op.drop_table("agent_memories")
    op.drop_index("ix_recommendations_customer_id", table_name="recommendations")
    op.drop_table("recommendations")
    op.drop_index("ix_fraud_analyses_transaction_id", table_name="fraud_analyses")
    op.drop_index("ix_fraud_analyses_customer_id", table_name="fraud_analyses")
    op.drop_table("fraud_analyses")
    op.drop_table("digital_wealth_twins")
    op.drop_table("behavior_profiles")
    op.drop_index("ix_transactions_customer_id", table_name="transactions")
    op.drop_table("transactions")
    op.drop_table("customers")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
