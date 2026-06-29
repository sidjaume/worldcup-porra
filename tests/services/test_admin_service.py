from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.domain.enums import NextSlot, TournamentStage
from app.services.admin_service import AdminService
from app.services.errors import ValidationError
from app.services.fixture_sync_service import SyncResult


class FakeDb:
    def __init__(self) -> None:
        self.rolled_back = False
        self.committed = False

    def add(self, item) -> None:
        self.item = item

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True

    def refresh(self, item) -> None:
        pass


class FakeTournamentsRepository:
    def __init__(self, *, tournament_id, team=None, match=None, next_match=None) -> None:
        self.tournament_id = tournament_id
        self.team = team
        self.match = match
        self.next_match = next_match

    def get_tournament(self, tournament_id):
        if tournament_id == self.tournament_id:
            return SimpleNamespace(id=tournament_id)
        return None

    def get_team(self, team_id):
        if self.team and team_id == self.team.id:
            return self.team
        return None

    def get_match(self, match_id):
        if self.match and match_id == self.match.id:
            return self.match
        if self.next_match and match_id == self.next_match.id:
            return self.next_match
        return None


def service_with_repo(repo: FakeTournamentsRepository) -> AdminService:
    service = AdminService(
        FakeDb(),
        SimpleNamespace(admin_emails=["admin@example.com"], scoring_version="test"),
    )
    service.tournaments = repo
    return service


def test_create_match_rejects_team_from_another_tournament() -> None:
    tournament_id = uuid4()
    other_tournament_id = uuid4()
    team = SimpleNamespace(id=uuid4(), tournament_id=other_tournament_id)
    service = service_with_repo(
        FakeTournamentsRepository(tournament_id=tournament_id, team=team)
    )

    with pytest.raises(ValidationError):
        service.create_match(
            admin_email="admin@example.com",
            tournament_id=tournament_id,
            stage=TournamentStage.ROUND_OF_32,
            bracket_position=1,
            scheduled_at=datetime(2026, 7, 1, tzinfo=UTC),
            home_team_id=team.id,
        )


def test_create_match_rejects_next_match_from_another_tournament() -> None:
    tournament_id = uuid4()
    next_match = SimpleNamespace(id=uuid4(), tournament_id=uuid4())
    service = service_with_repo(
        FakeTournamentsRepository(tournament_id=tournament_id, next_match=next_match)
    )

    with pytest.raises(ValidationError):
        service.create_match(
            admin_email="admin@example.com",
            tournament_id=tournament_id,
            stage=TournamentStage.ROUND_OF_32,
            bracket_position=1,
            scheduled_at=datetime(2026, 7, 1, tzinfo=UTC),
            next_match_id=next_match.id,
            next_match_slot=NextSlot.HOME,
        )


def test_complete_match_allows_tied_score_with_explicit_advancing_winner() -> None:
    tournament_id = uuid4()
    home_team_id = uuid4()
    away_team_id = uuid4()
    match = SimpleNamespace(
        id=uuid4(),
        tournament_id=tournament_id,
        home_team_id=home_team_id,
        away_team_id=away_team_id,
        home_score=None,
        away_score=None,
        winner_team_id=None,
        status=None,
        next_match_id=None,
        next_match_slot=None,
        sync_source=None,
        admin_override=False,
    )
    service = service_with_repo(
        FakeTournamentsRepository(tournament_id=tournament_id, match=match)
    )
    service.prediction_service = SimpleNamespace(score_match_predictions=lambda _: None)

    completed = service.complete_match(
        admin_email="admin@example.com",
        match_id=match.id,
        home_score=1,
        away_score=1,
        winner_team_id=home_team_id,
    )

    assert completed.home_score == 1
    assert completed.away_score == 1
    assert completed.winner_team_id == home_team_id
    assert completed.admin_override is True


def test_sync_provider_data_rolls_back_when_a_phase_reports_errors(monkeypatch) -> None:
    tournament_id = uuid4()
    db = FakeDb()
    repo = FakeTournamentsRepository(tournament_id=tournament_id)
    service = AdminService(
        db,
        SimpleNamespace(admin_emails=["admin@example.com"], scoring_version="test"),
    )
    service.tournaments = repo

    class FakeSyncService:
        def __init__(self, db, settings) -> None:  # noqa: ARG002
            pass

        def import_teams(self, tournament_id, adapter, year, commit=False):  # noqa: ARG002
            return SyncResult(teams_created=1)

        def import_matches(self, tournament_id, adapter, year, commit=False):  # noqa: ARG002
            return SyncResult(matches_created=1, errors=["bad payload"])

        def sync_results(self, tournament_id, adapter, year, commit=False):  # noqa: ARG002
            raise AssertionError("should not be called after errors")

    monkeypatch.setattr("app.services.admin_service.FixtureSyncService", FakeSyncService)

    result = service.sync_provider_data(
        admin_email="admin@example.com",
        tournament_id=tournament_id,
        adapter=SimpleNamespace(),
    )

    assert result.teams_created == 1
    assert result.matches_created == 1
    assert result.errors == ["bad payload"]
    assert db.rolled_back is True
    assert db.committed is False
