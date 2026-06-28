from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.auth import AuthExchangeCode, AuthSession


class AuthRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_exchange_code(
        self,
        *,
        code_hash: str,
        user_id: UUID,
        redirect_uri: str,
        expires_at: datetime,
    ) -> AuthExchangeCode:
        code = AuthExchangeCode(
            code_hash=code_hash,
            user_id=user_id,
            redirect_uri=redirect_uri,
            expires_at=expires_at,
            created_at=datetime.now(UTC),
        )
        self.db.add(code)
        self.db.flush()
        return code

    def consume_exchange_code(self, code_hash: str) -> AuthExchangeCode | None:
        code = self.db.scalar(
            select(AuthExchangeCode).where(AuthExchangeCode.code_hash == code_hash)
        )
        if code is None or code.consumed_at is not None:
            return None
        if code.expires_at <= datetime.now(UTC):
            return None
        code.consumed_at = datetime.now(UTC)
        self.db.flush()
        return code

    def create_session(
        self,
        *,
        user_id: UUID,
        refresh_token_hash: str,
        expires_at: datetime,
    ) -> AuthSession:
        session = AuthSession(
            user_id=user_id,
            refresh_token_hash=refresh_token_hash,
            expires_at=expires_at,
            created_at=datetime.now(UTC),
        )
        self.db.add(session)
        self.db.flush()
        return session

    def get_active_session(self, refresh_token_hash: str) -> AuthSession | None:
        session = self.db.scalar(
            select(AuthSession).where(AuthSession.refresh_token_hash == refresh_token_hash)
        )
        if session is None or session.revoked_at is not None:
            return None
        if session.expires_at <= datetime.now(UTC):
            return None
        return session

    def revoke_session(self, session: AuthSession) -> None:
        session.revoked_at = datetime.now(UTC)
        self.db.flush()

