"""Add predicted advancing winner to predictions

Revision ID: 20260629_0003
Revises: 20260629_0002
Create Date: 2026-06-29
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "20260629_0003"
down_revision: str | Sequence[str] | None = "20260629_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "predictions",
        sa.Column(
            "predicted_winner_team_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )
    op.create_foreign_key(
        "fk_predictions_predicted_winner_team_id_teams",
        "predictions",
        "teams",
        ["predicted_winner_team_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_predictions_predicted_winner_team_id_teams",
        "predictions",
        type_="foreignkey",
    )
    op.drop_column("predictions", "predicted_winner_team_id")
