from datetime import UTC, datetime, timedelta
from typing import Any
from urllib.parse import urlencode, urlparse
from uuid import UUID

import httpx
from sqlalchemy.orm import Session

from app.config.settings import Settings
from app.repositories.auth import AuthRepository
from app.repositories.users import UsersRepository
from app.services.errors import UnauthorizedError, ValidationError
from app.services.security import SecurityService


class AuthService:
    google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    google_token_url = "https://oauth2.googleapis.com/token"
    google_userinfo_url = "https://openidconnect.googleapis.com/v1/userinfo"

    def __init__(self, db: Session, settings: Settings) -> None:
        self.db = db
        self.settings = settings
        self.security = SecurityService(settings)
        self.auth_repo = AuthRepository(db)
        self.users_repo = UsersRepository(db)

    def google_start_url(self, redirect_uri: str) -> str:
        self._validate_frontend_redirect(redirect_uri)
        state = self.security.sign_state(redirect_uri=redirect_uri)
        params = {
            "client_id": self.settings.google_client_id,
            "redirect_uri": self.settings.google_redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "access_type": "offline",
            "prompt": "select_account",
        }
        return f"{self.google_auth_url}?{urlencode(params)}"

    def handle_google_callback(self, *, code: str, state: str) -> tuple[str, str]:
        state_payload = self.security.verify_state(state)
        redirect_uri = str(state_payload["redirect_uri"])
        self._validate_frontend_redirect(redirect_uri)

        identity = self._fetch_google_identity(code)
        user = self.users_repo.upsert_google_user(
            subject=str(identity["sub"]),
            email=str(identity["email"]),
            display_name=str(identity.get("name") or identity["email"]),
            avatar_url=identity.get("picture"),
        )
        exchange_code = self.security.create_exchange_code()
        self.auth_repo.create_exchange_code(
            code_hash=self.security.token_hash(exchange_code),
            user_id=user.id,
            redirect_uri=redirect_uri,
            expires_at=datetime.now(UTC) + timedelta(minutes=5),
        )
        self.db.commit()
        return redirect_uri, exchange_code

    def exchange_code(self, code: str) -> dict[str, Any]:
        exchange = self.auth_repo.consume_exchange_code(self.security.token_hash(code))
        if exchange is None:
            raise UnauthorizedError("Invalid or expired exchange code.")
        user = self.users_repo.get(exchange.user_id)
        if user is None or not user.is_active:
            raise UnauthorizedError("User is not active.")
        tokens = self._issue_tokens(user_id=user.id, email=user.email)
        self.db.commit()
        return {
            **tokens,
            "user": user,
        }

    def refresh(self, refresh_token: str) -> dict[str, str | int]:
        token_hash = self.security.token_hash(refresh_token)
        session = self.auth_repo.get_active_session(token_hash)
        if session is None:
            raise UnauthorizedError("Invalid refresh token.")
        user = self.users_repo.get(session.user_id)
        if user is None or not user.is_active:
            raise UnauthorizedError("User is not active.")

        self.auth_repo.revoke_session(session)
        tokens = self._issue_tokens(user_id=user.id, email=user.email)
        self.db.commit()
        return tokens

    def logout(self, refresh_token: str) -> None:
        session = self.auth_repo.get_active_session(
            self.security.token_hash(refresh_token)
        )
        if session is not None:
            self.auth_repo.revoke_session(session)
            self.db.commit()

    def verify_access_token(self, token: str) -> UUID:
        payload = self.security.decode_access_token(token)
        try:
            return UUID(str(payload["sub"]))
        except (KeyError, ValueError) as exc:
            raise UnauthorizedError("Invalid authentication token.") from exc

    def _issue_tokens(self, *, user_id: UUID, email: str) -> dict[str, str | int]:
        access_token = self.security.create_access_token(user_id=user_id, email=email)
        refresh_token = self.security.create_refresh_token()
        self.auth_repo.create_session(
            user_id=user_id,
            refresh_token_hash=self.security.token_hash(refresh_token),
            expires_at=datetime.now(UTC)
            + timedelta(days=self.settings.refresh_token_expire_days),
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.settings.access_token_expire_minutes * 60,
        }

    def _fetch_google_identity(self, code: str) -> dict[str, Any]:
        if not self.settings.google_client_id or not self.settings.google_client_secret:
            raise ValidationError("Google OAuth is not configured.")

        try:
            with httpx.Client(timeout=10) as client:
                token_response = client.post(
                    self.google_token_url,
                    data={
                        "code": code,
                        "client_id": self.settings.google_client_id,
                        "client_secret": self.settings.google_client_secret,
                        "redirect_uri": self.settings.google_redirect_uri,
                        "grant_type": "authorization_code",
                    },
                )
                token_response.raise_for_status()
                access_token = token_response.json()["access_token"]
                user_response = client.get(
                    self.google_userinfo_url,
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                user_response.raise_for_status()
                identity = user_response.json()
        except (httpx.HTTPError, KeyError, ValueError) as exc:
            raise UnauthorizedError("Google OAuth authentication failed.") from exc

        if not identity.get("email_verified", False):
            raise UnauthorizedError("Google account email is not verified.")
        return identity

    def _validate_frontend_redirect(self, redirect_uri: str) -> None:
        allowed = urlparse(self.settings.frontend_base_url)
        candidate = urlparse(redirect_uri)
        if (
            candidate.scheme not in {"http", "https"}
            or candidate.scheme != allowed.scheme
            or candidate.netloc != allowed.netloc
        ):
            raise ValidationError("Invalid frontend redirect URI.")
