"""Add provider audit fields to matches and teams

Revision ID: 20260629_0002
Revises: 20260628_0001
Create Date: 2026-06-29
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "20260629_0002"
down_revision: str | Sequence[str] | None = "20260628_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # matches: provider / audit columns
    op.add_column("matches", sa.Column("provider_ref", sa.Text(), nullable=True))
    op.add_column(
        "matches",
        sa.Column("provider_last_synced_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column("matches", sa.Column("sync_source", sa.Text(), nullable=True))
    op.add_column(
        "matches",
        sa.Column(
            "admin_override",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.create_unique_constraint(
        "uq_match_tournament_provider_ref",
        "matches",
        ["tournament_id", "provider_ref"],
    )

    # teams: provider reference column
    op.add_column("teams", sa.Column("provider_ref", sa.Text(), nullable=True))
    op.create_unique_constraint(
        "uq_team_tournament_provider_ref",
        "teams",
        ["tournament_id", "provider_ref"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_team_tournament_provider_ref",
        "teams",
        type_="unique",
    )
    op.drop_column("teams", "provider_ref")

    op.drop_constraint(
        "uq_match_tournament_provider_ref",
        "matches",
        type_="unique",
    )
    op.drop_column("matches", "admin_override")
    op.drop_column("matches", "sync_source")
    op.drop_column("matches", "provider_last_synced_at")
    op.drop_column("matches", "provider_ref")
