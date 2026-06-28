from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import MatchStatus, NextSlot, TournamentStage
from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


def enum_values(enum_cls: type) -> list[str]:
    return [item.value for item in enum_cls]


class Match(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "matches"
    __table_args__ = (
        UniqueConstraint(
            "tournament_id",
            "stage",
            "bracket_position",
            name="uq_match_tournament_stage_position",
        ),
        CheckConstraint("home_score IS NULL OR home_score >= 0", name="home_score_non_negative"),
        CheckConstraint("away_score IS NULL OR away_score >= 0", name="away_score_non_negative"),
        CheckConstraint(
            "home_team_id IS NULL OR away_team_id IS NULL OR home_team_id <> away_team_id",
            name="different_teams",
        ),
    )

    tournament_id: Mapped[UUID] = mapped_column(ForeignKey("tournaments.id"), nullable=False)
    stage: Mapped[TournamentStage] = mapped_column(
        Enum(
            TournamentStage,
            name="tournament_stage",
            values_callable=enum_values,
        ),
        nullable=False,
    )
    bracket_position: Mapped[int] = mapped_column(Integer, nullable=False)
    home_team_id: Mapped[UUID | None] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("teams.id"),
    )
    away_team_id: Mapped[UUID | None] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("teams.id"),
    )
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[MatchStatus] = mapped_column(
        Enum(MatchStatus, name="match_status", values_callable=enum_values),
        nullable=False,
        default=MatchStatus.SCHEDULED,
    )
    home_score: Mapped[int | None] = mapped_column(Integer)
    away_score: Mapped[int | None] = mapped_column(Integer)
    winner_team_id: Mapped[UUID | None] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("teams.id"),
    )
    next_match_id: Mapped[UUID | None] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("matches.id"),
    )
    next_match_slot: Mapped[NextSlot | None] = mapped_column(
        Enum(NextSlot, name="next_slot", values_callable=enum_values),
    )

    tournament: Mapped["Tournament"] = relationship(back_populates="matches")
    home_team: Mapped["Team | None"] = relationship(foreign_keys=[home_team_id])
    away_team: Mapped["Team | None"] = relationship(foreign_keys=[away_team_id])
    winner_team: Mapped["Team | None"] = relationship(foreign_keys=[winner_team_id])
    next_match: Mapped["Match | None"] = relationship(remote_side="Match.id")

