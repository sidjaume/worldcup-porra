from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import OAuthAccount, User


class UsersRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, user_id: UUID) -> User | None:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        return self.db.scalar(select(User).where(User.email == email))

    def get_by_provider(self, provider: str, provider_subject: str) -> User | None:
        return self.db.scalar(
            select(User)
            .join(OAuthAccount)
            .where(
                OAuthAccount.provider == provider,
                OAuthAccount.provider_subject == provider_subject,
            )
        )

    def upsert_google_user(
        self,
        *,
        subject: str,
        email: str,
        display_name: str,
        avatar_url: str | None,
    ) -> User:
        user = self.get_by_provider("google", subject)
        if user is None:
            user = self.get_by_email(email)

        if user is None:
            user = User(
                email=email,
                display_name=display_name,
                avatar_url=avatar_url,
                is_active=True,
            )
            self.db.add(user)
            self.db.flush()
        else:
            user.email = email
            user.display_name = display_name or user.display_name
            user.avatar_url = avatar_url

        account = self.db.scalar(
            select(OAuthAccount).where(
                OAuthAccount.provider == "google",
                OAuthAccount.provider_subject == subject,
            )
        )
        if account is None:
            self.db.add(
                OAuthAccount(
                    user_id=user.id,
                    provider="google",
                    provider_subject=subject,
                    provider_email=email,
                )
            )
        else:
            account.provider_email = email
        self.db.flush()
        return user

