import sys
from types import SimpleNamespace
from uuid import uuid4

import scripts.sync_knockout_fixtures as sync_script


class FakeSession:
    def __init__(self) -> None:
        self.committed = False
        self.rolled_back = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True


class FakeService:
    def __init__(self, db, settings) -> None:  # noqa: ARG002
        self.db = db

    def import_teams(self, tournament_id, adapter, year, commit=False):  # noqa: ARG002
        return sync_script.SyncResult(teams_created=1)

    def import_matches(self, tournament_id, adapter, year, commit=False):  # noqa: ARG002
        return sync_script.SyncResult(matches_created=1, errors=["bad payload"])

    def sync_results(self, tournament_id, adapter, year, commit=False):  # noqa: ARG002
        raise AssertionError("should not be called after errors")


class FakeAdapter:
    def __init__(self, *args, **kwargs) -> None:  # noqa: ARG002
        pass


def test_main_rolls_back_when_later_phase_fails(monkeypatch, capsys) -> None:
    session = FakeSession()
    monkeypatch.setattr(sync_script, "SessionLocal", lambda: session)
    monkeypatch.setattr(
        sync_script,
        "get_settings",
        lambda: SimpleNamespace(
            tournament_provider_base_url="https://example.test",
            tournament_provider_timeout_seconds=10,
            tournament_provider_api_key="",
        ),
    )
    monkeypatch.setattr(sync_script, "WorldCup2026Adapter", FakeAdapter)
    monkeypatch.setattr(sync_script, "FixtureSyncService", FakeService)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "sync_knockout_fixtures",
            str(uuid4()),
            "--mode",
            "all",
        ],
    )

    exit_code = sync_script.main()
    output = capsys.readouterr().out

    assert exit_code == 1
    assert session.rolled_back is True
    assert session.committed is False
    assert "errors=1" in output
    assert "bad payload" in output
