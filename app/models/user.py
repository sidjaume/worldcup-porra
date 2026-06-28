from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import CITEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(CITEXT(), nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(Text, nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    oauth_accounts: Mapped[list["OAuthAccount"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class OAuthAccount(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "oauth_accounts"
    __table_args__ = (
        UniqueConstraint("provider", "provider_subject", name="uq_oauth_provider_subject"),
    )

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    provider_subject: Mapped[str] = mapped_column(String(255), nullable=False)
    provider_email: Mapped[str] = mapped_column(CITEXT(), nullable=False)

    user: Mapped[User] = relationship(back_populates="oauth_accounts")
