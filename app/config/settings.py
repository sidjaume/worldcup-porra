from functools import lru_cache
from typing import Annotated, Literal

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
    frontend_base_url: str = "http://localhost:8501"
    backend_base_url: str = "http://localhost:8000"
    allowed_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["http://localhost:8501"]
    )
    admin_emails: Annotated[list[str], NoDecode] = Field(default_factory=list)
    scoring_version: str = "mvp-2026-v1"
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

    @field_validator("frontend_base_url", "backend_base_url")
    @classmethod
    def strip_trailing_slash(cls, value: str) -> str:
        return value.rstrip("/")

    def validate_production_secrets(self) -> None:
        if self.environment != "production":
            return
        missing = [
            name
            for name in (
                "database_url",
                "secret_key",
                "google_client_id",
                "google_client_secret",
                "google_redirect_uri",
            )
            if not getattr(self, name)
        ]
        if missing:
            missing_list = ", ".join(missing)
            raise RuntimeError(f"Missing production settings: {missing_list}")
        if self.secret_key == "dev-secret-change-me":
            raise RuntimeError("SECRET_KEY must be changed in production.")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.validate_production_secrets()
    return settings
