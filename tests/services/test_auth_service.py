from types import SimpleNamespace

import pytest

from app.services.auth_service import AuthService
from app.services.errors import ValidationError


def settings() -> SimpleNamespace:
    return SimpleNamespace(
        access_token_expire_minutes=15,
        frontend_base_url="http://localhost:8501",
        google_client_id="client-id",
        google_client_secret="client-secret",
        google_redirect_uri="http://localhost:8000/api/v1/auth/google/callback",
        refresh_token_expire_days=30,
        secret_key="test-secret",
    )


def test_google_start_accepts_frontend_redirect_on_same_origin() -> None:
    url = AuthService(None, settings()).google_start_url(
        "http://localhost:8501/auth/callback"
    )

    assert url.startswith(AuthService.google_auth_url)
    assert "client_id=client-id" in url


def test_google_start_rejects_redirect_on_different_origin() -> None:
    with pytest.raises(ValidationError):
        AuthService(None, settings()).google_start_url(
            "http://localhost:8501.evil.example/auth/callback"
        )


def test_google_start_rejects_redirect_with_different_scheme() -> None:
    with pytest.raises(ValidationError):
        AuthService(None, settings()).google_start_url(
            "https://localhost:8501/auth/callback"
        )
