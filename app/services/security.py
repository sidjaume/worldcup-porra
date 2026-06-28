from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any
from uuid import UUID

import jwt

from app.services.errors import UnauthorizedError

if TYPE_CHECKING:
    from app.config.settings import Settings


class SecurityService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def create_access_token(self, *, user_id: UUID, email: str) -> str:
        now = datetime.now(UTC)
        payload = {
            "sub": str(user_id),
            "email": email,
            "iat": int(now.timestamp()),
            "exp": int(
                (now + timedelta(minutes=self.settings.access_token_expire_minutes))
                .timestamp()
            ),
            "jti": secrets.token_urlsafe(16),
        }
        return jwt.encode(payload, self.settings.secret_key, algorithm="HS256")

    def decode_access_token(self, token: str) -> dict[str, Any]:
        try:
            return jwt.decode(token, self.settings.secret_key, algorithms=["HS256"])
        except jwt.PyJWTError as exc:
            raise UnauthorizedError("Invalid authentication token.") from exc

    def create_refresh_token(self) -> str:
        return secrets.token_urlsafe(48)

    def create_exchange_code(self) -> str:
        return secrets.token_urlsafe(32)

    def create_invite_code(self) -> str:
        alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
        first = "".join(secrets.choice(alphabet) for _ in range(4))
        second = "".join(secrets.choice(alphabet) for _ in range(4))
        return f"{first}-{second}"

    def token_hash(self, token: str) -> str:
        digest = hmac.new(
            self.settings.secret_key.encode("utf-8"),
            token.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return digest

    def sign_state(self, *, redirect_uri: str) -> str:
        now = datetime.now(UTC)
        payload = {
            "redirect_uri": redirect_uri,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=10)).timestamp()),
            "nonce": secrets.token_urlsafe(16),
        }
        return jwt.encode(payload, self.settings.secret_key, algorithm="HS256")

    def verify_state(self, state: str) -> dict[str, Any]:
        try:
            return jwt.decode(state, self.settings.secret_key, algorithms=["HS256"])
        except jwt.PyJWTError as exc:
            raise UnauthorizedError("Invalid OAuth state.") from exc
