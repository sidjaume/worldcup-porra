from datetime import UTC, datetime

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config.settings import Settings
from app.domain.enums import MatchStatus, NextSlot, PoolRole, TournamentStage
from app.models.match import Match
from app.models.pool import Pool, PoolParticipant
from app.models.prediction import Prediction, PredictionScore
from app.models.team import Team
from app.models.tournament import Tournament
from app.models.user import User
from app.providers.base import ProviderMatch, ProviderTeam
from app.providers.worldcup2026 import ProviderError
from app.services.fixture_sync_service import FixtureSyncService


pytestmark = pytest.mark.integration


class StaticAdapter:
    def __init__(
        self,
        *,
        teams: list[ProviderTeam],
        matches: list[ProviderMatch],
    ) -> None:
        self._teams = teams
        self._matches = matches

    def fetch_teams(self, tournament_year: int) -> list[ProviderTeam]:
        return self._teams

    def fetch_matches(self, tournament_year: int) -> list[ProviderMatch]:
        return self._matches


class FailingMatchFetchAdapter(StaticAdapter):
    def fetch_matches(self, tournament_year: int) -> list[ProviderMatch]:
        raise ProviderError("Provider match m73 has unknown status 'abandoned'.")


def test_import_teams_and_matches_is_idempotent(db_session: Session) -> None:
    tournament = _create_tournament(db_session, name="Import Idempotency")
    db_session.commit()
    adapter = StaticAdapter(
        teams=[
            ProviderTeam(provider_ref="esp", name="Spain", fifa_code="ESP"),
            ProviderTeam(provider_ref="por", name="Portugal", fifa_code="POR"),
        ],
        matches=[
            ProviderMatch(
                provider_ref="m73",
                stage=TournamentStage.ROUND_OF_32,
                bracket_position=1,
                scheduled_at=datetime(2026, 6, 28, 18, tzinfo=UTC),
                status=MatchStatus.SCHEDULED,
                home_team_provider_ref="esp",
                away_team_provider_ref="por",
            )
        ],
    )
    service = FixtureSyncService(db_session, Settings(_env_file=None))

    first = service.import_teams(tournament.id, adapter)
    first.merge(service.import_matches(tournament.id, adapter))
    second = service.import_teams(tournament.id, adapter)
    second.merge(service.import_matches(tournament.id, adapter))

    assert first.teams_created == 2
    assert first.matches_created == 1
    assert second.teams_created == 0
    assert second.matches_created == 0
    assert second.matches_updated == 0
    assert db_session.scalar(select(func.count(Team.id))) == 2
    assert db_session.scalar(select(func.count(Match.id))) == 1


def test_completed_tied_result_scores_and_advances_idempotently(
    db_session: Session,
) -> None:
    context = _create_scoring_context(db_session)
    adapter = StaticAdapter(
        teams=[],
        matches=[
            ProviderMatch(
                provider_ref="m73",
                stage=TournamentStage.ROUND_OF_32,
                bracket_position=1,
                scheduled_at=context.match.scheduled_at,
                status=MatchStatus.COMPLETED,
                home_team_provider_ref="esp",
                away_team_provider_ref="por",
                home_score=1,
                away_score=1,
                winner_provider_ref="esp",
            )
        ],
    )
    service = FixtureSyncService(db_session, Settings(_env_file=None))

    first = service.sync_results(context.tournament.id, adapter)
    second = service.sync_results(context.tournament.id, adapter)
    db_session.refresh(context.match)
    db_session.refresh(context.next_match)

    score = db_session.scalar(
        select(PredictionScore).where(
            PredictionScore.prediction_id == context.prediction.id
        )
    )
    assert first.errors == []
    assert first.matches_updated == 1
    assert second.errors == []
    assert second.matches_updated == 0
    assert context.match.status == MatchStatus.COMPLETED
    assert context.match.home_score == 1
    assert context.match.away_score == 1
    assert context.match.winner_team_id == context.home_team.id
    assert context.next_match.home_team_id == context.home_team.id
    assert score is not None
    assert score.points == 3
    assert score.correct_winner is True
    assert score.partial_away_goals is True
    assert db_session.scalar(select(func.count(PredictionScore.id))) == 1


def test_provider_progression_skips_downstream_admin_override(
    db_session: Session,
) -> None:
    context = _create_scoring_context(db_session)
    manual_team = _create_team(db_session, context.tournament, "France", "fra")
    context.next_match.home_team = manual_team
    context.next_match.sync_source = "admin"
    context.next_match.admin_override = True
    db_session.commit()
    adapter = StaticAdapter(
        teams=[],
        matches=[
            ProviderMatch(
                provider_ref="m73",
                stage=TournamentStage.ROUND_OF_32,
                bracket_position=1,
                scheduled_at=context.match.scheduled_at,
                status=MatchStatus.COMPLETED,
                home_team_provider_ref="esp",
                away_team_provider_ref="por",
                home_score=2,
                away_score=1,
                winner_provider_ref="esp",
            )
        ],
    )

    result = FixtureSyncService(db_session, Settings(_env_file=None)).sync_results(
        context.tournament.id,
        adapter,
    )
    db_session.refresh(context.match)
    db_session.refresh(context.next_match)

    assert result.errors == []
    assert context.match.status == MatchStatus.COMPLETED
    assert context.next_match.home_team_id == manual_team.id
    assert context.next_match.sync_source == "admin"
    assert context.next_match.admin_override is True


def test_provider_progression_allows_empty_downstream_slot(
    db_session: Session,
) -> None:
    context = _create_scoring_context(db_session)
    adapter = StaticAdapter(
        teams=[],
        matches=[
            ProviderMatch(
                provider_ref="m73",
                stage=TournamentStage.ROUND_OF_32,
                bracket_position=1,
                scheduled_at=context.match.scheduled_at,
                status=MatchStatus.COMPLETED,
                home_team_provider_ref="esp",
                away_team_provider_ref="por",
                home_score=2,
                away_score=1,
                winner_provider_ref="esp",
            )
        ],
    )

    result = FixtureSyncService(db_session, Settings(_env_file=None)).sync_results(
        context.tournament.id,
        adapter,
    )
    db_session.refresh(context.next_match)

    assert result.errors == []
    assert context.next_match.home_team_id == context.home_team.id
    assert context.next_match.admin_override is False


def test_provider_progression_allows_same_team_downstream_slot(
    db_session: Session,
) -> None:
    context = _create_scoring_context(db_session)
    context.next_match.home_team = context.home_team
    db_session.commit()
    adapter = StaticAdapter(
        teams=[],
        matches=[
            ProviderMatch(
                provider_ref="m73",
                stage=TournamentStage.ROUND_OF_32,
                bracket_position=1,
                scheduled_at=context.match.scheduled_at,
                status=MatchStatus.COMPLETED,
                home_team_provider_ref="esp",
                away_team_provider_ref="por",
                home_score=2,
                away_score=1,
                winner_provider_ref="esp",
            )
        ],
    )

    result = FixtureSyncService(db_session, Settings(_env_file=None)).sync_results(
        context.tournament.id,
        adapter,
    )
    db_session.refresh(context.next_match)

    assert result.errors == []
    assert context.next_match.home_team_id == context.home_team.id
    assert context.next_match.admin_override is False


def test_provider_progression_reports_conflict_without_overwrite(
    db_session: Session,
) -> None:
    context = _create_scoring_context(db_session)
    conflicting_team = _create_team(db_session, context.tournament, "France", "fra")
    context.next_match.home_team = conflicting_team
    db_session.commit()
    adapter = StaticAdapter(
        teams=[],
        matches=[
            ProviderMatch(
                provider_ref="m73",
                stage=TournamentStage.ROUND_OF_32,
                bracket_position=1,
                scheduled_at=context.match.scheduled_at,
                status=MatchStatus.COMPLETED,
                home_team_provider_ref="esp",
                away_team_provider_ref="por",
                home_score=2,
                away_score=1,
                winner_provider_ref="esp",
            )
        ],
    )

    result = FixtureSyncService(db_session, Settings(_env_file=None)).sync_results(
        context.tournament.id,
        adapter,
    )
    db_session.refresh(context.match)
    db_session.refresh(context.next_match)

    assert result.errors
    assert "would overwrite a populated home slot" in result.errors[0]
    assert context.match.status == MatchStatus.SCHEDULED
    assert context.match.home_score is None
    assert context.match.away_score is None
    assert context.match.winner_team_id is None
    assert context.next_match.home_team_id == conflicting_team.id


def test_invalid_completed_provider_result_does_not_dirty_match(
    db_session: Session,
) -> None:
    tournament = _create_tournament(db_session, name="Invalid Provider Result")
    home = _create_team(db_session, tournament, "Spain", "esp")
    away = _create_team(db_session, tournament, "Portugal", "por")
    match = _create_match(db_session, tournament, home, away)
    db_session.commit()
    adapter = StaticAdapter(
        teams=[],
        matches=[
            ProviderMatch(
                provider_ref="m73",
                stage=TournamentStage.ROUND_OF_32,
                bracket_position=1,
                scheduled_at=match.scheduled_at,
                status=MatchStatus.COMPLETED,
                home_team_provider_ref="esp",
                away_team_provider_ref="por",
                home_score=None,
                away_score=None,
                winner_provider_ref="esp",
            )
        ],
    )

    result = FixtureSyncService(db_session, Settings(_env_file=None)).sync_results(
        tournament.id,
        adapter,
    )
    db_session.refresh(match)

    assert result.errors
    assert match.status == MatchStatus.SCHEDULED
    assert match.home_score is None
    assert match.away_score is None
    assert match.winner_team_id is None


def test_provider_normalization_error_does_not_dirty_match(
    db_session: Session,
) -> None:
    tournament = _create_tournament(db_session, name="Provider Normalization Error")
    home = _create_team(db_session, tournament, "Spain", "esp")
    away = _create_team(db_session, tournament, "Portugal", "por")
    match = _create_match(db_session, tournament, home, away)
    db_session.commit()
    adapter = FailingMatchFetchAdapter(teams=[], matches=[])

    result = FixtureSyncService(db_session, Settings(_env_file=None)).sync_results(
        tournament.id,
        adapter,
    )
    db_session.refresh(match)

    assert result.errors
    assert "unknown status" in result.errors[0]
    assert match.status == MatchStatus.SCHEDULED
    assert match.home_score is None
    assert match.away_score is None
    assert match.winner_team_id is None


def test_completed_result_rolls_back_if_late_sync_step_fails(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = _create_scoring_context(db_session)
    adapter = StaticAdapter(
        teams=[],
        matches=[
            ProviderMatch(
                provider_ref="m73",
                stage=TournamentStage.ROUND_OF_32,
                bracket_position=1,
                scheduled_at=context.match.scheduled_at,
                status=MatchStatus.COMPLETED,
                home_team_provider_ref="esp",
                away_team_provider_ref="por",
                home_score=1,
                away_score=1,
                winner_provider_ref="esp",
            )
        ],
    )
    service = FixtureSyncService(db_session, Settings(_env_file=None))

    def boom(self, match):  # noqa: ARG001
        raise RuntimeError("scoring failed")

    monkeypatch.setattr(
        "app.services.fixture_sync_service.PredictionService.score_match_predictions",
        boom,
    )

    result = service.sync_results(context.tournament.id, adapter)
    db_session.refresh(context.match)

    assert result.errors
    assert context.match.status == MatchStatus.SCHEDULED
    assert context.match.home_score is None
    assert context.match.away_score is None
    assert context.match.winner_team_id is None
    assert db_session.scalar(select(func.count(PredictionScore.id))) == 0


class ScoringContext:
    def __init__(
        self,
        *,
        tournament: Tournament,
        home_team: Team,
        away_team: Team,
        match: Match,
        next_match: Match,
        prediction: Prediction,
    ) -> None:
        self.tournament = tournament
        self.home_team = home_team
        self.away_team = away_team
        self.match = match
        self.next_match = next_match
        self.prediction = prediction


def _create_scoring_context(db_session: Session) -> ScoringContext:
    tournament = _create_tournament(db_session, name="Scoring Sync")
    home = _create_team(db_session, tournament, "Spain", "esp")
    away = _create_team(db_session, tournament, "Portugal", "por")
    match = _create_match(db_session, tournament, home, away)
    next_match = Match(
        tournament=tournament,
        stage=TournamentStage.ROUND_OF_16,
        bracket_position=1,
        scheduled_at=datetime(2026, 7, 4, 18, tzinfo=UTC),
        status=MatchStatus.SCHEDULED,
    )
    db_session.add(next_match)
    db_session.flush()
    match.next_match_id = next_match.id
    match.next_match_slot = NextSlot.HOME

    user = User(email="owner-sync@example.com", display_name="Owner", is_active=True)
    db_session.add(user)
    db_session.flush()
    pool = Pool(
        tournament_id=tournament.id,
        owner_user_id=user.id,
        name="Sync Pool",
        invite_code_hash="sync-pool-invite",
        invite_code_last_rotated_at=datetime.now(UTC),
        is_active=True,
    )
    db_session.add(pool)
    db_session.flush()
    db_session.add(
        PoolParticipant(
            pool_id=pool.id,
            user_id=user.id,
            role=PoolRole.OWNER,
            joined_at=datetime.now(UTC),
        )
    )
    prediction = Prediction(
        pool_id=pool.id,
        user_id=user.id,
        match_id=match.id,
        predicted_home_goals=2,
        predicted_away_goals=1,
        submitted_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db_session.add(prediction)
    db_session.commit()
    return ScoringContext(
        tournament=tournament,
        home_team=home,
        away_team=away,
        match=match,
        next_match=next_match,
        prediction=prediction,
    )


def _create_tournament(db_session: Session, *, name: str) -> Tournament:
    tournament = Tournament(name=name, year=2026)
    db_session.add(tournament)
    return tournament


def _create_team(
    db_session: Session,
    tournament: Tournament,
    name: str,
    provider_ref: str,
) -> Team:
    team = Team(tournament=tournament, name=name, provider_ref=provider_ref)
    db_session.add(team)
    return team


def _create_match(
    db_session: Session,
    tournament: Tournament,
    home: Team,
    away: Team,
) -> Match:
    match = Match(
        tournament=tournament,
        stage=TournamentStage.ROUND_OF_32,
        bracket_position=1,
        home_team=home,
        away_team=away,
        scheduled_at=datetime(2026, 6, 28, 18, tzinfo=UTC),
        status=MatchStatus.SCHEDULED,
        provider_ref="m73",
    )
    db_session.add(match)
    return match
