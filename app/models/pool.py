from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import ParticipantStatus, PoolRole
from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.match import enum_values

if TYPE_CHECKING:
    from app.models.user import User


class Pool(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "pools"

    tournament_id: Mapped[UUID] = mapped_column(ForeignKey("tournaments.id"), nullable=False)
    owner_user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    invite_code_hash: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    invite_code_last_rotated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    participants: Mapped[list["PoolParticipant"]] = relationship(
        back_populates="pool",
        cascade="all, delete-orphan",
    )


class PoolParticipant(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "pool_participants"
    __table_args__ = (
        UniqueConstraint("pool_id", "user_id", name="uq_pool_participant_pool_user"),
    )

    pool_id: Mapped[UUID] = mapped_column(ForeignKey("pools.id", ondelete="CASCADE"))
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    role: Mapped[PoolRole] = mapped_column(
        Enum(PoolRole, name="pool_role", values_callable=enum_values),
        nullable=False,
        default=PoolRole.PARTICIPANT,
    )
    status: Mapped[ParticipantStatus] = mapped_column(
        Enum(ParticipantStatus, name="participant_status", values_callable=enum_values),
        nullable=False,
        default=ParticipantStatus.ACTIVE,
    )
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    removed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    pool: Mapped[Pool] = relationship(back_populates="participants")
    user: Mapped["User"] = relationship()

