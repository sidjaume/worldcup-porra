from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.domain.enums import MatchStatus, NextSlot, TournamentStage
from app.services.admin_service import AdminService
from app.services.errors import ForbiddenError, ValidationError
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
    def __init__(
        self,
        *,
        tournament_id,
        team=None,
        teams=None,
        match=None,
        next_match=None,
    ) -> None:
        self.tournament_id = tournament_id
        self.teams = list(teams or ([team] if team else []))
        self.match = match
        self.next_match = next_match

    def get_tournament(self, tournament_id):
        if tournament_id == self.tournament_id:
            return SimpleNamespace(id=tournament_id)
        return None

    def get_team(self, team_id):
        for team in self.teams:
            if team_id == team.id:
                return team
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


def test_complete_match_marks_downstream_slot_as_admin_override_when_changed() -> None:
    tournament_id = uuid4()
    home_team_id = uuid4()
    away_team_id = uuid4()
    next_match = SimpleNamespace(
        id=uuid4(),
        tournament_id=tournament_id,
        home_team_id=None,
        away_team_id=None,
        sync_source="provider",
        admin_override=False,
    )
    match = SimpleNamespace(
        id=uuid4(),
        tournament_id=tournament_id,
        home_team_id=home_team_id,
        away_team_id=away_team_id,
        home_score=None,
        away_score=None,
        winner_team_id=None,
        status=None,
        next_match_id=next_match.id,
        next_match_slot=NextSlot.HOME,
        sync_source=None,
        admin_override=False,
    )
    service = service_with_repo(
        FakeTournamentsRepository(
            tournament_id=tournament_id,
            match=match,
            next_match=next_match,
        )
    )
    service.prediction_service = SimpleNamespace(score_match_predictions=lambda _: None)

    service.complete_match(
        admin_email="admin@example.com",
        match_id=match.id,
        home_score=2,
        away_score=1,
        winner_team_id=home_team_id,
    )

    assert next_match.home_team_id == home_team_id
    assert next_match.sync_source == "admin"
    assert next_match.admin_override is True


def test_update_match_teams_requires_admin() -> None:
    tournament_id = uuid4()
    match = SimpleNamespace(
        id=uuid4(),
        tournament_id=tournament_id,
        home_team_id=None,
        away_team_id=None,
        status=MatchStatus.SCHEDULED,
    )
    service = service_with_repo(
        FakeTournamentsRepository(tournament_id=tournament_id, match=match)
    )

    with pytest.raises(ForbiddenError):
        service.update_match_teams(
            admin_email="user@example.com",
            match_id=match.id,
            home_team_id=None,
            update_home_team=True,
        )


def test_update_match_teams_rejects_empty_update() -> None:
    tournament_id = uuid4()
    match = SimpleNamespace(
        id=uuid4(),
        tournament_id=tournament_id,
        home_team_id=None,
        away_team_id=None,
        status=MatchStatus.SCHEDULED,
    )
    service = service_with_repo(
        FakeTournamentsRepository(tournament_id=tournament_id, match=match)
    )

    with pytest.raises(ValidationError):
        service.update_match_teams(
            admin_email="admin@example.com",
            match_id=match.id,
        )

    assert service.db.committed is False


def test_update_match_teams_sets_override_and_preserves_other_match_state() -> None:
    tournament_id = uuid4()
    old_home = SimpleNamespace(id=uuid4(), tournament_id=tournament_id)
    new_home = SimpleNamespace(id=uuid4(), tournament_id=tournament_id)
    away = SimpleNamespace(id=uuid4(), tournament_id=tournament_id)
    next_match_id = uuid4()
    scheduled_at = datetime(2026, 7, 1, tzinfo=UTC)
    match = SimpleNamespace(
        id=uuid4(),
        tournament_id=tournament_id,
        home_team_id=old_home.id,
        away_team_id=away.id,
        home_team=old_home,
        away_team=away,
        scheduled_at=scheduled_at,
        status=MatchStatus.LOCKED,
        home_score=2,
        away_score=1,
        winner_team_id=old_home.id,
        next_match_id=next_match_id,
        next_match_slot=NextSlot.HOME,
        sync_source="provider",
        admin_override=False,
    )
    service = service_with_repo(
        FakeTournamentsRepository(
            tournament_id=tournament_id,
            teams=[old_home, new_home, away],
            match=match,
        )
    )

    updated = service.update_match_teams(
        admin_email="admin@example.com",
        match_id=match.id,
        home_team_id=new_home.id,
        update_home_team=True,
    )

    assert updated.home_team_id == new_home.id
    assert updated.away_team_id == away.id
    assert updated.home_team == new_home
    assert updated.away_team == away
    assert updated.status == MatchStatus.LOCKED
    assert updated.scheduled_at == scheduled_at
    assert updated.home_score == 2
    assert updated.away_score == 1
    assert updated.winner_team_id == old_home.id
    assert updated.next_match_id == next_match_id
    assert updated.next_match_slot == NextSlot.HOME
    assert updated.sync_source == "admin"
    assert updated.admin_override is True
    assert service.db.committed is True


def test_update_match_teams_can_clear_an_unresolved_slot() -> None:
    tournament_id = uuid4()
    away = SimpleNamespace(id=uuid4(), tournament_id=tournament_id)
    match = SimpleNamespace(
        id=uuid4(),
        tournament_id=tournament_id,
        home_team_id=None,
        away_team_id=away.id,
        home_team=None,
        away_team=away,
        status=MatchStatus.SCHEDULED,
        sync_source="provider",
        admin_override=False,
    )
    service = service_with_repo(
        FakeTournamentsRepository(
            tournament_id=tournament_id,
            teams=[away],
            match=match,
        )
    )

    updated = service.update_match_teams(
        admin_email="admin@example.com",
        match_id=match.id,
        away_team_id=None,
        update_away_team=True,
    )

    assert updated.home_team_id is None
    assert updated.away_team_id is None
    assert updated.away_team is None
    assert updated.sync_source == "admin"
    assert updated.admin_override is True


def test_update_match_teams_rejects_duplicate_known_teams() -> None:
    tournament_id = uuid4()
    team = SimpleNamespace(id=uuid4(), tournament_id=tournament_id)
    match = SimpleNamespace(
        id=uuid4(),
        tournament_id=tournament_id,
        home_team_id=team.id,
        away_team_id=None,
        status=MatchStatus.SCHEDULED,
    )
    service = service_with_repo(
        FakeTournamentsRepository(tournament_id=tournament_id, teams=[team], match=match)
    )

    with pytest.raises(ValidationError):
        service.update_match_teams(
            admin_email="admin@example.com",
            match_id=match.id,
            away_team_id=team.id,
            update_away_team=True,
        )

    assert service.db.committed is False


def test_update_match_teams_rejects_team_from_another_tournament() -> None:
    tournament_id = uuid4()
    team = SimpleNamespace(id=uuid4(), tournament_id=uuid4())
    match = SimpleNamespace(
        id=uuid4(),
        tournament_id=tournament_id,
        home_team_id=None,
        away_team_id=None,
        status=MatchStatus.SCHEDULED,
    )
    service = service_with_repo(
        FakeTournamentsRepository(tournament_id=tournament_id, teams=[team], match=match)
    )

    with pytest.raises(ValidationError):
        service.update_match_teams(
            admin_email="admin@example.com",
            match_id=match.id,
            home_team_id=team.id,
            update_home_team=True,
        )


def test_update_match_teams_rejects_completed_match() -> None:
    tournament_id = uuid4()
    match = SimpleNamespace(
        id=uuid4(),
        tournament_id=tournament_id,
        home_team_id=None,
        away_team_id=None,
        status=MatchStatus.COMPLETED,
    )
    service = service_with_repo(
        FakeTournamentsRepository(tournament_id=tournament_id, match=match)
    )

    with pytest.raises(ValidationError):
        service.update_match_teams(
            admin_email="admin@example.com",
            match_id=match.id,
            home_team_id=None,
            update_home_team=True,
        )


def test_update_match_status_sets_override_and_preserves_other_match_state() -> None:
    tournament_id = uuid4()
    home_team_id = uuid4()
    away_team_id = uuid4()
    next_match_id = uuid4()
    scheduled_at = datetime(2026, 7, 1, tzinfo=UTC)
    match = SimpleNamespace(
        id=uuid4(),
        tournament_id=tournament_id,
        home_team_id=home_team_id,
        away_team_id=away_team_id,
        scheduled_at=scheduled_at,
        status=MatchStatus.SCHEDULED,
        home_score=1,
        away_score=0,
        winner_team_id=home_team_id,
        next_match_id=next_match_id,
        next_match_slot=NextSlot.AWAY,
        sync_source="provider",
        admin_override=False,
    )
    service = service_with_repo(
        FakeTournamentsRepository(tournament_id=tournament_id, match=match)
    )

    updated = service.update_match_status(
        admin_email="admin@example.com",
        match_id=match.id,
        status=MatchStatus.IN_PROGRESS,
    )

    assert updated.status == MatchStatus.IN_PROGRESS
    assert updated.home_team_id == home_team_id
    assert updated.away_team_id == away_team_id
    assert updated.scheduled_at == scheduled_at
    assert updated.home_score == 1
    assert updated.away_score == 0
    assert updated.winner_team_id == home_team_id
    assert updated.next_match_id == next_match_id
    assert updated.next_match_slot == NextSlot.AWAY
    assert updated.sync_source == "admin"
    assert updated.admin_override is True
    assert service.db.committed is True


@pytest.mark.parametrize(
    "status",
    [
        MatchStatus.SCHEDULED,
        MatchStatus.LOCKED,
        MatchStatus.IN_PROGRESS,
        MatchStatus.CANCELLED,
    ],
)
def test_update_match_status_accepts_operational_statuses(status: MatchStatus) -> None:
    tournament_id = uuid4()
    match = SimpleNamespace(
        id=uuid4(),
        tournament_id=tournament_id,
        status=MatchStatus.SCHEDULED,
        sync_source=None,
        admin_override=False,
    )
    service = service_with_repo(
        FakeTournamentsRepository(tournament_id=tournament_id, match=match)
    )

    updated = service.update_match_status(
        admin_email="admin@example.com",
        match_id=match.id,
        status=status,
    )

    assert updated.status == status


def test_update_match_status_rejects_completed_status() -> None:
    tournament_id = uuid4()
    match = SimpleNamespace(
        id=uuid4(),
        tournament_id=tournament_id,
        status=MatchStatus.SCHEDULED,
        sync_source=None,
        admin_override=False,
    )
    service = service_with_repo(
        FakeTournamentsRepository(tournament_id=tournament_id, match=match)
    )

    with pytest.raises(ValidationError):
        service.update_match_status(
            admin_email="admin@example.com",
            match_id=match.id,
            status=MatchStatus.COMPLETED,
        )

    assert service.db.committed is False


def test_update_match_status_rejects_completed_match() -> None:
    tournament_id = uuid4()
    match = SimpleNamespace(
        id=uuid4(),
        tournament_id=tournament_id,
        status=MatchStatus.COMPLETED,
        sync_source=None,
        admin_override=False,
    )
    service = service_with_repo(
        FakeTournamentsRepository(tournament_id=tournament_id, match=match)
    )

    with pytest.raises(ValidationError):
        service.update_match_status(
            admin_email="admin@example.com",
            match_id=match.id,
            status=MatchStatus.SCHEDULED,
        )

    assert service.db.committed is False


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
