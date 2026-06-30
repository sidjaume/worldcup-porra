from functools import lru_cache
from typing import Annotated, Literal
from uuid import UUID
from urllib.parse import urlparse

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: Literal["development", "test", "production"] = "development"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/worldcup_pool"
    secret_key: str = "dev-secret-change-me"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = ""
    frontend_base_url: str = "http://localhost:3000"
    backend_base_url: str = "http://localhost:8000"
    allowed_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["http://localhost:3000"]
    )
    admin_emails: Annotated[list[str], NoDecode] = Field(default_factory=list)
    scoring_version: str = "mvp-2026-v1"
    tournament_provider_base_url: str = "https://worldcup26.ir/get"
    tournament_provider_api_key: str = ""
    tournament_provider_timeout_seconds: int = 10
    cron_secret: str = ""
    tournament_sync_tournament_id: UUID | None = None
    tournament_sync_year: int = 2026
    tournament_sync_mode: Literal["all", "teams", "matches", "results"] = "all"
    log_level: str = "INFO"

    @field_validator("database_url")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+psycopg://", 1)
        return value

    @field_validator("allowed_origins", "admin_emails", mode="before")
    @classmethod
    def parse_csv(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @field_validator(
        "frontend_base_url",
        "backend_base_url",
        "tournament_provider_base_url",
    )
    @classmethod
    def strip_trailing_slash(cls, value: str) -> str:
        return value.rstrip("/")

    def validate_production_secrets(self) -> None:
        if self.environment != "production":
            return
        required_settings = (
            "database_url",
            "secret_key",
            "google_client_id",
            "google_client_secret",
            "google_redirect_uri",
            "frontend_base_url",
            "backend_base_url",
            "allowed_origins",
        )
        missing = [
            name
            for name in required_settings
            if name not in self.model_fields_set or not getattr(self, name)
        ]
        if missing:
            missing_list = ", ".join(missing)
            raise RuntimeError(f"Missing production settings: {missing_list}")
        if self.secret_key == "dev-secret-change-me":
            raise RuntimeError("SECRET_KEY must be changed in production.")
        local_url_settings = (
            "database_url",
            "google_redirect_uri",
            "frontend_base_url",
            "backend_base_url",
        )
        local_settings = [
            name
            for name in local_url_settings
            if self._is_local_url(getattr(self, name))
        ]
        if any(self._is_local_url(origin) for origin in self.allowed_origins):
            local_settings.append("allowed_origins")
        if local_settings:
            local_list = ", ".join(local_settings)
            raise RuntimeError(
                f"Production settings must not use localhost URLs: {local_list}"
            )

    @staticmethod
    def _is_local_url(value: str) -> bool:
        hostname = urlparse(value).hostname
        return hostname in {"localhost", "127.0.0.1", "::1"}


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.validate_production_secrets()
    return settings
