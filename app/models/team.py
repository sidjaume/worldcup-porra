from uuid import UUID

from sqlalchemy import ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Team(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "teams"
    __table_args__ = (
        UniqueConstraint("tournament_id", "name", name="uq_team_tournament_name"),
        UniqueConstraint("tournament_id", "fifa_code", name="uq_team_tournament_fifa_code"),
    )

    tournament_id: Mapped[UUID] = mapped_column(ForeignKey("tournaments.id"), nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    short_name: Mapped[str | None] = mapped_column(Text)
    fifa_code: Mapped[str | None] = mapped_column(Text)
    flag_url: Mapped[str | None] = mapped_column(Text)

    tournament: Mapped["Tournament"] = relationship(back_populates="teams")
