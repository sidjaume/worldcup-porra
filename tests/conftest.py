from collections.abc import Iterator
from contextlib import contextmanager
import os
from pathlib import Path
import re
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, make_url
from sqlalchemy.exc import DBAPIError, OperationalError


LOCAL_DATABASE_URL = (
    "postgresql+psycopg://worldcup:worldcup@localhost:5432/worldcup_pool"
)
EXPLICIT_TEST_URL_ENV_VARS = ("TEST_DATABASE_URL", "INTEGRATION_DATABASE_URL")
SAFE_LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1", "db", "postgres", "host.docker.internal"}
GENERATED_DATABASE_RE = re.compile(r"^[A-Za-z0-9_]+$")


@pytest.fixture
def temporary_database_url() -> Iterator[str]:
    database_url, source = _integration_database_candidate()
    url = _normalize_postgres_url(database_url)
    if not _is_safe_database_url(url, source):
        pytest.skip(
            "Integration database URL must point to a local Postgres server or "
            "an explicit test database."
        )

    database_name = f"{url.database or 'worldcup_pool'}_it_{uuid4().hex[:8]}"
    if not GENERATED_DATABASE_RE.fullmatch(database_name):
        pytest.skip("Integration database name is not safe for temporary database creation.")

    admin_engine = create_engine(
        _render_url(url.set(database="postgres")),
        isolation_level="AUTOCOMMIT",
        pool_pre_ping=True,
        connect_args={"connect_timeout": 2},
    )
    quoted_database_name = f'"{database_name}"'

    try:
        with admin_engine.connect() as connection:
            connection.execute(text(f"CREATE DATABASE {quoted_database_name}"))
    except (DBAPIError, OperationalError) as exc:
        admin_engine.dispose()
        pytest.skip(f"Local integration database is unavailable: {exc.__class__.__name__}")

    try:
        yield _render_url(url.set(database=database_name))
    finally:
        try:
            with admin_engine.connect() as connection:
                connection.execute(
                    text(
                        """
                        SELECT pg_terminate_backend(pid)
                        FROM pg_stat_activity
                        WHERE datname = :database_name
                        AND pid <> pg_backend_pid()
                        """
                    ),
                    {"database_name": database_name},
                )
                connection.execute(text(f"DROP DATABASE IF EXISTS {quoted_database_name}"))
        finally:
            admin_engine.dispose()


@pytest.fixture
def migrated_database_url(temporary_database_url: str) -> Iterator[str]:
    _run_alembic(temporary_database_url, "upgrade", "head")
    yield temporary_database_url


@pytest.fixture
def db_session(migrated_database_url: str):
    from sqlalchemy.orm import sessionmaker

    engine = create_engine(migrated_database_url, pool_pre_ping=True)
    SessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def run_alembic(database_url: str, action: str, revision: str) -> None:
    _run_alembic(database_url, action, revision)


def _integration_database_candidate() -> tuple[str, str]:
    for env_var in (*EXPLICIT_TEST_URL_ENV_VARS, "DATABASE_URL"):
        value = os.getenv(env_var)
        if value:
            return value, env_var
    return LOCAL_DATABASE_URL, "LOCAL_DATABASE_URL"


def _normalize_postgres_url(database_url: str) -> URL:
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return make_url(database_url)


def _is_safe_database_url(url: URL, source: str) -> bool:
    if not url.drivername.startswith("postgresql"):
        return False
    host = url.host or ""
    database = (url.database or "").lower()
    if host in SAFE_LOCAL_HOSTS:
        return True
    return source in EXPLICIT_TEST_URL_ENV_VARS and "test" in database


def _render_url(url: URL) -> str:
    return url.render_as_string(hide_password=False)


def _run_alembic(database_url: str, action: str, revision: str) -> None:
    from app.config.settings import get_settings

    root = Path(__file__).resolve().parents[1]
    config = Config(str(root / "alembic.ini"))
    config.set_main_option("script_location", str(root / "app" / "db" / "migrations"))

    with _database_settings(database_url):
        get_settings.cache_clear()
        try:
            getattr(command, action)(config, revision)
        finally:
            get_settings.cache_clear()


@contextmanager
def _database_settings(database_url: str) -> Iterator[None]:
    old_database_url = os.environ.get("DATABASE_URL")
    old_environment = os.environ.get("ENVIRONMENT")
    os.environ["DATABASE_URL"] = database_url
    os.environ["ENVIRONMENT"] = "test"
    try:
        yield
    finally:
        if old_database_url is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = old_database_url
        if old_environment is None:
            os.environ.pop("ENVIRONMENT", None)
        else:
            os.environ["ENVIRONMENT"] = old_environment
