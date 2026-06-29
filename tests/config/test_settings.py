import pytest

from app.config.settings import Settings


CONFIG_ENV_VARS = (
    "ENVIRONMENT",
    "DATABASE_URL",
    "SECRET_KEY",
    "GOOGLE_CLIENT_ID",
    "GOOGLE_CLIENT_SECRET",
    "GOOGLE_REDIRECT_URI",
    "FRONTEND_BASE_URL",
    "BACKEND_BASE_URL",
    "ALLOWED_ORIGINS",
)


@pytest.fixture(autouse=True)
def clear_settings_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in CONFIG_ENV_VARS:
        monkeypatch.delenv(name, raising=False)


def production_settings(**overrides: object) -> Settings:
    values = {
        "environment": "production",
        "database_url": "postgresql+psycopg://user:pass@db.example.com/app",
        "secret_key": "prod-secret",
        "google_client_id": "client-id",
        "google_client_secret": "client-secret",
        "google_redirect_uri": (
            "https://api.example.com/api/v1/auth/google/callback"
        ),
        "frontend_base_url": "https://app.example.com",
        "backend_base_url": "https://api.example.com",
        "allowed_origins": ["https://app.example.com"],
    }
    values.update(overrides)
    return Settings(_env_file=None, **values)


def test_default_frontend_settings_use_nextjs_localhost() -> None:
    settings = Settings(_env_file=None)

    assert settings.frontend_base_url == "http://localhost:3000"
    assert settings.allowed_origins == ["http://localhost:3000"]
    assert settings.backend_base_url == "http://localhost:8000"


def test_production_requires_explicit_runtime_urls_and_origins() -> None:
    settings = Settings(
        _env_file=None,
        environment="production",
        database_url="postgresql+psycopg://user:pass@db.example.com/app",
        secret_key="prod-secret",
        google_client_id="client-id",
        google_client_secret="client-secret",
        google_redirect_uri="https://api.example.com/api/v1/auth/google/callback",
    )

    with pytest.raises(RuntimeError, match="frontend_base_url"):
        settings.validate_production_secrets()


def test_production_rejects_localhost_runtime_urls() -> None:
    settings = production_settings(frontend_base_url="http://localhost:3000")

    with pytest.raises(RuntimeError, match="frontend_base_url"):
        settings.validate_production_secrets()


def test_production_accepts_complete_external_configuration() -> None:
    production_settings().validate_production_secrets()
