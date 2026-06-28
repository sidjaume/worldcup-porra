from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.match import Match
    from app.models.team import Team


class Tournament(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "tournaments"
    __table_args__ = (UniqueConstraint("year", "name", name="uq_tournament_year_name"),)

    name: Mapped[str] = mapped_column(Text, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    teams: Mapped[list["Team"]] = relationship(back_populates="tournament")
    matches: Mapped[list["Match"]] = relationship(back_populates="tournament")

