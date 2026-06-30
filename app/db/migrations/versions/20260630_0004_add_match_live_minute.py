"""Add live minute to matches

Revision ID: 20260630_0004
Revises: 20260629_0003
Create Date: 2026-06-30
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "20260630_0004"
down_revision: str | Sequence[str] | None = "20260629_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("matches", sa.Column("live_minute", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("matches", "live_minute")
