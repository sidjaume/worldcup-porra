from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import PredictionStatus
from app.models.base import Base, UUIDPrimaryKeyMixin
from app.models.match import enum_values

if TYPE_CHECKING:
    from app.models.match import Match
    from app.models.pool import Pool
    from app.models.team import Team
    from app.models.user import User


class Prediction(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "predictions"
    __table_args__ = (
        UniqueConstraint("pool_id", "user_id", "match_id", name="uq_prediction_pool_user_match"),
        CheckConstraint("predicted_home_goals >= 0", name="predicted_home_goals_non_negative"),
        CheckConstraint("predicted_away_goals >= 0", name="predicted_away_goals_non_negative"),
    )

    pool_id: Mapped[UUID] = mapped_column(ForeignKey("pools.id"), nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    match_id: Mapped[UUID] = mapped_column(ForeignKey("matches.id"), nullable=False)
    predicted_home_goals: Mapped[int] = mapped_column(Integer, nullable=False)
    predicted_away_goals: Mapped[int] = mapped_column(Integer, nullable=False)
    predicted_winner_team_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("teams.id"),
        nullable=True,
    )
    status: Mapped[PredictionStatus] = mapped_column(
        Enum(PredictionStatus, name="prediction_status", values_callable=enum_values),
        nullable=False,
        default=PredictionStatus.EDITABLE,
    )
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    user: Mapped["User"] = relationship()
    pool: Mapped["Pool"] = relationship()
    match: Mapped["Match"] = relationship()
    predicted_winner_team: Mapped["Team | None"] = relationship()
    score: Mapped["PredictionScore | None"] = relationship(
        back_populates="prediction",
        cascade="all, delete-orphan",
        uselist=False,
    )


class PredictionScore(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "prediction_scores"
    __table_args__ = (
        CheckConstraint("points >= 0", name="points_non_negative"),
    )

    prediction_id: Mapped[UUID] = mapped_column(
        ForeignKey("predictions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    points: Mapped[int] = mapped_column(Integer, nullable=False)
    correct_winner: Mapped[bool] = mapped_column(nullable=False, default=False)
    exact_score: Mapped[bool] = mapped_column(nullable=False, default=False)
    partial_home_goals: Mapped[bool] = mapped_column(nullable=False, default=False)
    partial_away_goals: Mapped[bool] = mapped_column(nullable=False, default=False)
    scoring_version: Mapped[str] = mapped_column(nullable=False)
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    prediction: Mapped[Prediction] = relationship(back_populates="score")

