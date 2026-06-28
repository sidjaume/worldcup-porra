"""initial backend schema

Revision ID: 20260628_0001
Revises:
Create Date: 2026-06-28
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260628_0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


tournament_stage = postgresql.ENUM(
    "round_of_32",
    "round_of_16",
    "quarter_final",
    "semi_final",
    "final",
    name="tournament_stage",
)
match_status = postgresql.ENUM(
    "scheduled",
    "locked",
    "in_progress",
    "completed",
    "cancelled",
    name="match_status",
)
pool_role = postgresql.ENUM("owner", "participant", name="pool_role")
participant_status = postgresql.ENUM("active", "removed", name="participant_status")
next_slot = postgresql.ENUM("home", "away", name="next_slot")
prediction_status = postgresql.ENUM("editable", "locked", "scored", name="prediction_status")


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.execute("CREATE EXTENSION IF NOT EXISTS citext")

    bind = op.get_bind()
    tournament_stage.create(bind, checkfirst=True)
    match_status.create(bind, checkfirst=True)
    pool_role.create(bind, checkfirst=True)
    participant_status.create(bind, checkfirst=True)
    next_slot.create(bind, checkfirst=True)
    prediction_status.create(bind, checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", postgresql.CITEXT(), nullable=False),
        sa.Column("display_name", sa.Text(), nullable=False),
        sa.Column("avatar_url", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_table(
        "oauth_accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("provider_subject", sa.String(length=255), nullable=False),
        sa.Column("provider_email", postgresql.CITEXT(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("provider", "provider_subject", name="uq_oauth_provider_subject"),
    )
    op.create_table(
        "tournaments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("year", "name", name="uq_tournament_year_name"),
    )
    op.create_table(
        "teams",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tournament_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("short_name", sa.Text(), nullable=True),
        sa.Column("fifa_code", sa.Text(), nullable=True),
        sa.Column("flag_url", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["tournament_id"], ["tournaments.id"]),
        sa.UniqueConstraint("tournament_id", "name", name="uq_team_tournament_name"),
        sa.UniqueConstraint("tournament_id", "fifa_code", name="uq_team_tournament_fifa_code"),
    )
    op.create_table(
        "matches",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tournament_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("stage", tournament_stage, nullable=False),
        sa.Column("bracket_position", sa.Integer(), nullable=False),
        sa.Column("home_team_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("away_team_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", match_status, nullable=False, server_default="scheduled"),
        sa.Column("home_score", sa.Integer(), nullable=True),
        sa.Column("away_score", sa.Integer(), nullable=True),
        sa.Column("winner_team_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("next_match_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("next_match_slot", next_slot, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("home_score IS NULL OR home_score >= 0", name="ck_matches_home_score_non_negative"),
        sa.CheckConstraint("away_score IS NULL OR away_score >= 0", name="ck_matches_away_score_non_negative"),
        sa.CheckConstraint("home_team_id IS NULL OR away_team_id IS NULL OR home_team_id <> away_team_id", name="ck_matches_different_teams"),
        sa.ForeignKeyConstraint(["away_team_id"], ["teams.id"]),
        sa.ForeignKeyConstraint(["home_team_id"], ["teams.id"]),
        sa.ForeignKeyConstraint(["next_match_id"], ["matches.id"]),
        sa.ForeignKeyConstraint(["tournament_id"], ["tournaments.id"]),
        sa.ForeignKeyConstraint(["winner_team_id"], ["teams.id"]),
        sa.UniqueConstraint("tournament_id", "stage", "bracket_position", name="uq_match_tournament_stage_position"),
    )
    op.create_index("ix_matches_scheduled_at", "matches", ["scheduled_at"])
    op.create_index("ix_matches_status", "matches", ["status"])
    op.create_table(
        "pools",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tournament_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("owner_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("invite_code_hash", sa.Text(), nullable=False),
        sa.Column("invite_code_last_rotated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["tournament_id"], ["tournaments.id"]),
        sa.UniqueConstraint("invite_code_hash", name="uq_pools_invite_code_hash"),
    )
    op.create_index("ix_pools_owner_user_id", "pools", ["owner_user_id"])
    op.create_index("ix_pools_tournament_id", "pools", ["tournament_id"])
    op.create_table(
        "pool_participants",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("pool_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", pool_role, nullable=False, server_default="participant"),
        sa.Column("status", participant_status, nullable=False, server_default="active"),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("removed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["pool_id"], ["pools.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("pool_id", "user_id", name="uq_pool_participant_pool_user"),
    )
    op.create_index("ix_pool_participants_pool_status", "pool_participants", ["pool_id", "status"])
    op.create_index("ix_pool_participants_user_status", "pool_participants", ["user_id", "status"])
    op.create_table(
        "predictions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("pool_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("match_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("predicted_home_goals", sa.Integer(), nullable=False),
        sa.Column("predicted_away_goals", sa.Integer(), nullable=False),
        sa.Column("status", prediction_status, nullable=False, server_default="editable"),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("predicted_home_goals >= 0", name="ck_predictions_predicted_home_goals_non_negative"),
        sa.CheckConstraint("predicted_away_goals >= 0", name="ck_predictions_predicted_away_goals_non_negative"),
        sa.ForeignKeyConstraint(["match_id"], ["matches.id"]),
        sa.ForeignKeyConstraint(["pool_id"], ["pools.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.UniqueConstraint("pool_id", "user_id", "match_id", name="uq_prediction_pool_user_match"),
    )
    op.create_index("ix_predictions_match_id", "predictions", ["match_id"])
    op.create_index("ix_predictions_pool_match", "predictions", ["pool_id", "match_id"])
    op.create_index("ix_predictions_user_pool", "predictions", ["user_id", "pool_id"])
    op.create_table(
        "prediction_scores",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("prediction_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False),
        sa.Column("correct_winner", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("exact_score", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("partial_home_goals", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("partial_away_goals", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("scoring_version", sa.Text(), nullable=False),
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("points >= 0", name="ck_prediction_scores_points_non_negative"),
        sa.ForeignKeyConstraint(["prediction_id"], ["predictions.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("prediction_id", name="uq_prediction_scores_prediction_id"),
    )
    op.create_table(
        "auth_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("refresh_token_hash", sa.Text(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("refresh_token_hash", name="uq_auth_sessions_refresh_token_hash"),
    )
    op.create_index("ix_auth_sessions_expires_at", "auth_sessions", ["expires_at"])
    op.create_index("ix_auth_sessions_user_id", "auth_sessions", ["user_id"])
    op.create_table(
        "auth_exchange_codes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("code_hash", sa.Text(), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("redirect_uri", sa.Text(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("code_hash", name="uq_auth_exchange_codes_code_hash"),
    )
    op.create_index("ix_auth_exchange_codes_expires_at", "auth_exchange_codes", ["expires_at"])


def downgrade() -> None:
    op.drop_index("ix_auth_exchange_codes_expires_at", table_name="auth_exchange_codes")
    op.drop_table("auth_exchange_codes")
    op.drop_index("ix_auth_sessions_user_id", table_name="auth_sessions")
    op.drop_index("ix_auth_sessions_expires_at", table_name="auth_sessions")
    op.drop_table("auth_sessions")
    op.drop_table("prediction_scores")
    op.drop_index("ix_predictions_user_pool", table_name="predictions")
    op.drop_index("ix_predictions_pool_match", table_name="predictions")
    op.drop_index("ix_predictions_match_id", table_name="predictions")
    op.drop_table("predictions")
    op.drop_index("ix_pool_participants_user_status", table_name="pool_participants")
    op.drop_index("ix_pool_participants_pool_status", table_name="pool_participants")
    op.drop_table("pool_participants")
    op.drop_index("ix_pools_tournament_id", table_name="pools")
    op.drop_index("ix_pools_owner_user_id", table_name="pools")
    op.drop_table("pools")
    op.drop_index("ix_matches_status", table_name="matches")
    op.drop_index("ix_matches_scheduled_at", table_name="matches")
    op.drop_table("matches")
    op.drop_table("teams")
    op.drop_table("tournaments")
    op.drop_table("oauth_accounts")
    op.drop_table("users")

    bind = op.get_bind()
    prediction_status.drop(bind, checkfirst=True)
    next_slot.drop(bind, checkfirst=True)
    participant_status.drop(bind, checkfirst=True)
    pool_role.drop(bind, checkfirst=True)
    match_status.drop(bind, checkfirst=True)
    tournament_stage.drop(bind, checkfirst=True)

