from collections.abc import Generator
from uuid import uuid4

from fastapi.testclient import TestClient

from app.api.dependencies import db_dependency, settings_dependency
from app.api.main import app
from app.api.routers.ops import _run_sync_mode
from app.config.settings import Settings
from app.services.fixture_sync_service import SyncResult


class FakeDb:
    def __init__(self) -> None:
        self.commits = 0
        self.rollbacks = 0

    def commit(self) -> None:
        self.commits += 1

    def rollback(self) -> None:
        self.rollbacks += 1


class FakeSyncService:
    def __init__(self) -> None:
        self.db = FakeDb()
        self.calls: list[str] = []
        self.fail_on: str | None = None

    def import_teams(self, tournament_id, adapter, year, commit=False):  # noqa: ARG002
        self.calls.append("teams")
        return self._result("teams")

    def import_matches(self, tournament_id, adapter, year, commit=False):  # noqa: ARG002
        self.calls.append("matches")
        return self._result("matches")

    def sync_results(self, tournament_id, adapter, year, commit=False):  # noqa: ARG002
        self.calls.append("results")
        return self._result("results")

    def _result(self, phase: str) -> SyncResult:
        if self.fail_on == phase:
            return SyncResult(errors=[f"{phase} failed"])
        result = SyncResult()
        if phase == "teams":
            result.teams_updated = 1
        if phase == "matches":
            result.matches_updated = 1
        return result


def override_db() -> Generator[object, None, None]:
    yield object()


def test_ops_sync_requires_cron_credentials() -> None:
    app.dependency_overrides[db_dependency] = override_db
    app.dependency_overrides[settings_dependency] = lambda: Settings(
        _env_file=None,
        cron_secret="cron-secret",
        tournament_sync_tournament_id=uuid4(),
    )
    try:
        response = TestClient(app).post("/api/v1/ops/sync")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 401
    assert response.json()["error"]["message"] == "Invalid cron credentials."


def test_ops_sync_requires_tournament_id_when_authorized() -> None:
    app.dependency_overrides[db_dependency] = override_db
    app.dependency_overrides[settings_dependency] = lambda: Settings(
        _env_file=None,
        cron_secret="cron-secret",
        tournament_sync_tournament_id=None,
    )
    try:
        response = TestClient(app).post(
            "/api/v1/ops/sync",
            headers={"Authorization": "Bearer cron-secret"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 400
    assert (
        response.json()["error"]["message"]
        == "TOURNAMENT_SYNC_TOURNAMENT_ID is not configured."
    )


def test_ops_sync_runs_configured_scheduler_sync(monkeypatch) -> None:
    tournament_id = uuid4()
    captured = {}

    def fake_run_sync_mode(**kwargs):
        captured.update(kwargs)
        return SyncResult(teams_updated=1, matches_updated=2)

    app.dependency_overrides[db_dependency] = override_db
    app.dependency_overrides[settings_dependency] = lambda: Settings(
        _env_file=None,
        cron_secret="cron-secret",
        tournament_sync_tournament_id=tournament_id,
        tournament_sync_year=2026,
        tournament_sync_mode="matches",
    )
    monkeypatch.setattr("app.api.routers.ops._run_sync_mode", fake_run_sync_mode)
    try:
        response = TestClient(app).post(
            "/api/v1/ops/sync",
            headers={"Authorization": "Bearer cron-secret"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "teams_created": 0,
        "teams_updated": 1,
        "matches_created": 0,
        "matches_updated": 2,
        "errors": [],
    }
    assert captured["tournament_id"] == tournament_id
    assert captured["year"] == 2026
    assert captured["mode"] == "matches"


def test_run_sync_mode_runs_configured_matches_phase_and_commits() -> None:
    service = FakeSyncService()

    result = _run_sync_mode(
        service=service,  # type: ignore[arg-type]
        tournament_id=uuid4(),
        adapter=object(),
        year=2026,
        mode="matches",
    )

    assert service.calls == ["matches"]
    assert result.matches_updated == 1
    assert service.db.commits == 1
    assert service.db.rollbacks == 0


def test_run_sync_mode_rolls_back_and_stops_on_phase_error() -> None:
    service = FakeSyncService()
    service.fail_on = "matches"

    result = _run_sync_mode(
        service=service,  # type: ignore[arg-type]
        tournament_id=uuid4(),
        adapter=object(),
        year=2026,
        mode="all",
    )

    assert service.calls == ["teams", "matches"]
    assert result.errors == ["matches failed"]
    assert service.db.commits == 0
    assert service.db.rollbacks == 1
