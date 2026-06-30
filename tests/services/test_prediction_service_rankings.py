from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.domain.enums import MatchStatus, ParticipantStatus
from app.models.prediction import Prediction
from app.services.errors import ValidationError
from app.services.prediction_service import PredictionService


class FakePoolsRepository:
    def __init__(self, *, pool_id, participant_user_id, tournament_id=None) -> None:
        self.pool_id = pool_id
        self.participant_user_id = participant_user_id
        self.tournament_id = tournament_id or uuid4()

    def get(self, pool_id):
        if pool_id == self.pool_id:
            return SimpleNamespace(
                id=pool_id,
                is_active=True,
                tournament_id=self.tournament_id,
            )
        return None

    def get_participant(self, *, pool_id, user_id):
        if pool_id == self.pool_id and user_id == self.participant_user_id:
            return SimpleNamespace(status=ParticipantStatus.ACTIVE)
        return None


class FakePredictionsRepository:
    def __init__(self, rows) -> None:
        self.rows = rows
        self.upsert_kwargs = None
        self.scored_rows = []

    def list_scored_rows(self, pool_id):
        return list(self.rows)

    def upsert_for_user(self, **kwargs):
        self.upsert_kwargs = kwargs
        return SimpleNamespace(**kwargs)

    def list_all_for_match(self, match_id):
        return list(self.rows)

    def upsert_score(self, **kwargs):
        self.scored_rows.append(kwargs)


def test_rankings_use_earliest_joined_at_as_final_tie_breaker() -> None:
    pool_id = uuid4()
    requesting_user_id = uuid4()
    earlier_user_id = uuid4()
    later_user_id = uuid4()

    later_user = SimpleNamespace(id=later_user_id, display_name="Alice")
    earlier_user = SimpleNamespace(id=earlier_user_id, display_name="Zoe")

    rows = [
        (
            later_user,
            8,
            2,
            3,
            4,
            5,
            datetime(2026, 6, 29, 13, tzinfo=UTC),
        ),
        (
            earlier_user,
            8,
            2,
            3,
            4,
            5,
            datetime(2026, 6, 29, 12, tzinfo=UTC),
        ),
    ]

    service = PredictionService(
        SimpleNamespace(),
        SimpleNamespace(scoring_version="test"),
    )
    service.pools = FakePoolsRepository(
        pool_id=pool_id,
        participant_user_id=requesting_user_id,
    )
    service.predictions = FakePredictionsRepository(rows)

    rankings = service.rankings(pool_id=pool_id, user_id=requesting_user_id)

    assert [row[0].id for row in rankings] == [earlier_user_id, later_user_id]


class FakeTournamentsRepository:
    def __init__(self, match) -> None:
        self.match = match

    def get_match(self, match_id):
        if match_id == self.match.id:
            return self.match
        return None


class FakeDb:
    def commit(self) -> None:
        pass


def test_submit_tied_prediction_persists_home_advancing_winner() -> None:
    pool_id = uuid4()
    user_id = uuid4()
    tournament_id = uuid4()
    home_team_id = uuid4()
    away_team_id = uuid4()
    match = _match(
        tournament_id=tournament_id,
        home_team_id=home_team_id,
        away_team_id=away_team_id,
    )
    service = _prediction_service(
        pool_id=pool_id,
        user_id=user_id,
        tournament_id=tournament_id,
        match=match,
    )

    prediction = service.submit_prediction(
        pool_id=pool_id,
        user_id=user_id,
        match_id=match.id,
        predicted_home_goals=1,
        predicted_away_goals=1,
        predicted_winner_team_id=home_team_id,
    )

    assert prediction.predicted_winner_team_id == home_team_id
    assert service.predictions.upsert_kwargs["predicted_winner_team_id"] == home_team_id


def test_submit_tied_prediction_persists_away_advancing_winner() -> None:
    pool_id = uuid4()
    user_id = uuid4()
    tournament_id = uuid4()
    home_team_id = uuid4()
    away_team_id = uuid4()
    match = _match(
        tournament_id=tournament_id,
        home_team_id=home_team_id,
        away_team_id=away_team_id,
    )
    service = _prediction_service(
        pool_id=pool_id,
        user_id=user_id,
        tournament_id=tournament_id,
        match=match,
    )

    prediction = service.submit_prediction(
        pool_id=pool_id,
        user_id=user_id,
        match_id=match.id,
        predicted_home_goals=2,
        predicted_away_goals=2,
        predicted_winner_team_id=away_team_id,
    )

    assert prediction.predicted_winner_team_id == away_team_id


def test_submit_tied_prediction_requires_advancing_winner() -> None:
    match = _match(tournament_id=uuid4(), home_team_id=uuid4(), away_team_id=uuid4())
    service = _prediction_service(
        pool_id=uuid4(),
        user_id=uuid4(),
        tournament_id=match.tournament_id,
        match=match,
    )

    with pytest.raises(ValidationError, match="required for tied predictions"):
        service.submit_prediction(
            pool_id=service.pools.pool_id,
            user_id=service.pools.participant_user_id,
            match_id=match.id,
            predicted_home_goals=1,
            predicted_away_goals=1,
        )


def test_submit_tied_prediction_rejects_unknown_match_teams() -> None:
    match = _match(tournament_id=uuid4(), home_team_id=None, away_team_id=uuid4())
    service = _prediction_service(
        pool_id=uuid4(),
        user_id=uuid4(),
        tournament_id=match.tournament_id,
        match=match,
    )

    with pytest.raises(ValidationError, match="before both teams are known"):
        service.submit_prediction(
            pool_id=service.pools.pool_id,
            user_id=service.pools.participant_user_id,
            match_id=match.id,
            predicted_home_goals=1,
            predicted_away_goals=1,
            predicted_winner_team_id=match.away_team_id,
        )


def test_submit_non_tied_prediction_rejects_provided_advancing_winner() -> None:
    match = _match(tournament_id=uuid4(), home_team_id=uuid4(), away_team_id=uuid4())
    service = _prediction_service(
        pool_id=uuid4(),
        user_id=uuid4(),
        tournament_id=match.tournament_id,
        match=match,
    )

    with pytest.raises(ValidationError, match="only allowed for tied predictions"):
        service.submit_prediction(
            pool_id=service.pools.pool_id,
            user_id=service.pools.participant_user_id,
            match_id=match.id,
            predicted_home_goals=2,
            predicted_away_goals=1,
            predicted_winner_team_id=match.home_team_id,
        )


def test_score_match_predictions_uses_tied_prediction_advancing_winner() -> None:
    home_team_id = uuid4()
    away_team_id = uuid4()
    match = _match(
        tournament_id=uuid4(),
        home_team_id=home_team_id,
        away_team_id=away_team_id,
        status=MatchStatus.COMPLETED,
        home_score=1,
        away_score=1,
        winner_team_id=away_team_id,
    )
    correct_prediction = Prediction(
        pool_id=uuid4(),
        user_id=uuid4(),
        match_id=match.id,
        predicted_home_goals=1,
        predicted_away_goals=1,
        predicted_winner_team_id=away_team_id,
        submitted_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    wrong_prediction = Prediction(
        pool_id=uuid4(),
        user_id=uuid4(),
        match_id=match.id,
        predicted_home_goals=1,
        predicted_away_goals=1,
        predicted_winner_team_id=home_team_id,
        submitted_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    service = PredictionService(FakeDb(), SimpleNamespace(scoring_version="test"))
    service.predictions = FakePredictionsRepository([correct_prediction, wrong_prediction])

    service.score_match_predictions(match)

    assert service.predictions.scored_rows[0]["points"] == 4
    assert service.predictions.scored_rows[0]["correct_winner"] is True
    assert service.predictions.scored_rows[1]["points"] == 2
    assert service.predictions.scored_rows[1]["correct_winner"] is False


def _prediction_service(*, pool_id, user_id, tournament_id, match):
    service = PredictionService(FakeDb(), SimpleNamespace(scoring_version="test"))
    service.pools = FakePoolsRepository(
        pool_id=pool_id,
        participant_user_id=user_id,
        tournament_id=tournament_id,
    )
    service.tournaments = FakeTournamentsRepository(match)
    service.predictions = FakePredictionsRepository([])
    return service


def _match(
    *,
    tournament_id,
    home_team_id,
    away_team_id,
    status=MatchStatus.SCHEDULED,
    home_score=None,
    away_score=None,
    winner_team_id=None,
):
    return SimpleNamespace(
        id=uuid4(),
        tournament_id=tournament_id,
        home_team_id=home_team_id,
        away_team_id=away_team_id,
        scheduled_at=datetime(2030, 7, 1, 18, tzinfo=UTC),
        status=status,
        home_score=home_score,
        away_score=away_score,
        winner_team_id=winner_team_id,
    )
