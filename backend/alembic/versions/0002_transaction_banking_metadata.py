"""Persist banking transaction semantics for runtime intelligence.

Revision ID: 0002_tx_metadata
Revises: 0001_initial
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_tx_metadata"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("transactions", sa.Column("transaction_type", sa.String(length=32), nullable=False, server_default="legacy"))
    op.add_column("transactions", sa.Column("category", sa.String(length=64), nullable=False, server_default="general"))
    op.add_column("transactions", sa.Column("merchant", sa.String(length=120), nullable=True))
    op.add_column("transactions", sa.Column("status", sa.String(length=32), nullable=False, server_default="completed"))


def downgrade() -> None:
    op.drop_column("transactions", "status")
    op.drop_column("transactions", "merchant")
    op.drop_column("transactions", "category")
    op.drop_column("transactions", "transaction_type")
