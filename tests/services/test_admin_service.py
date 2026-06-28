from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.domain.enums import NextSlot, TournamentStage
from app.services.admin_service import AdminService
from app.services.errors import ValidationError


class FakeDb:
    def add(self, item) -> None:
        self.item = item

    def commit(self) -> None:
        pass

    def refresh(self, item) -> None:
        pass


class FakeTournamentsRepository:
    def __init__(self, *, tournament_id, team=None, next_match=None) -> None:
        self.tournament_id = tournament_id
        self.team = team
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
