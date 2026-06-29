import pytest
from sqlalchemy import create_engine, inspect, text

from tests.conftest import run_alembic


pytestmark = pytest.mark.integration


def test_initial_migration_upgrades_and_downgrades_cleanly(
    temporary_database_url: str,
) -> None:
    run_alembic(temporary_database_url, "upgrade", "head")

    engine = create_engine(temporary_database_url, pool_pre_ping=True)
    try:
        inspector = inspect(engine)
        assert "users" in inspector.get_table_names()
        assert "predictions" in inspector.get_table_names()
        assert "alembic_version" in inspector.get_table_names()
    finally:
        engine.dispose()

    run_alembic(temporary_database_url, "downgrade", "base")

    engine = create_engine(temporary_database_url, pool_pre_ping=True)
    try:
        inspector = inspect(engine)
        remaining_tables = set(inspector.get_table_names())
        assert "users" not in remaining_tables
        assert "predictions" not in remaining_tables
        with engine.connect() as connection:
            version_count = connection.scalar(text("SELECT count(*) FROM alembic_version"))
        assert version_count == 0
    finally:
        engine.dispose()
