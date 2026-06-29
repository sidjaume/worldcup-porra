from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config.settings import Settings
from app.domain.enums import MatchStatus, ParticipantStatus, PoolRole, TournamentStage
from app.models.match import Match
from app.models.pool import PoolParticipant
from app.models.prediction import Prediction, PredictionScore
from app.models.team import Team
from app.models.tournament import Tournament
from app.models.user import User
from app.repositories.pools import PoolsRepository
from app.repositories.predictions import PredictionsRepository
from app.services.prediction_service import PredictionService


pytestmark = pytest.mark.integration


def test_pool_creation_adds_owner_membership_and_enforces_unique_members(
    db_session: Session,
) -> None:
    tournament = _create_tournament(db_session)
    owner = _create_user(db_session, "owner@example.com", "Owner")
    participant = _create_user(db_session, "participant@example.com", "Participant")
    db_session.flush()

    pools = PoolsRepository(db_session)
    pool = pools.create_pool(
        tournament_id=tournament.id,
        owner_user_id=owner.id,
        name="Office Pool",
        invite_code_hash="invite-hash",
    )
    pools.add_participant(pool_id=pool.id, user_id=participant.id)
    db_session.flush()

    owner_membership = pools.get_participant(pool_id=pool.id, user_id=owner.id)
    assert owner_membership is not None
    assert owner_membership.role == PoolRole.OWNER
    assert owner_membership.status == ParticipantStatus.ACTIVE
    assert pools.participant_count(pool.id) == 2

    listed_pool, listed_role, listed_count = pools.list_for_user(owner.id)[0]
    assert listed_pool.id == pool.id
    assert listed_role == PoolRole.OWNER
    assert listed_count == 2

    db_session.add(
        PoolParticipant(
            pool_id=pool.id,
            user_id=participant.id,
            role=PoolRole.PARTICIPANT,
            status=ParticipantStatus.ACTIVE,
            joined_at=datetime.now(UTC),
        )
    )
    with pytest.raises(IntegrityError):
        db_session.flush()


def test_prediction_upsert_updates_existing_row_and_preserves_uniqueness(
    db_session: Session,
) -> None:
    context = _create_prediction_context(db_session)
    predictions = PredictionsRepository(db_session)

    created = predictions.upsert_for_user(
        pool_id=context.pool_id,
        user_id=context.user.id,
        match_id=context.match.id,
        predicted_home_goals=1,
        predicted_away_goals=0,
    )
    first_id = created.id
    first_submitted_at = created.submitted_at

    updated = predictions.upsert_for_user(
        pool_id=context.pool_id,
        user_id=context.user.id,
        match_id=context.match.id,
        predicted_home_goals=2,
        predicted_away_goals=1,
    )

    assert updated.id == first_id
    assert updated.submitted_at == first_submitted_at
    assert updated.updated_at >= first_submitted_at
    assert updated.predicted_home_goals == 2
    assert updated.predicted_away_goals == 1
    assert db_session.scalar(select(func.count(Prediction.id))) == 1


def test_rankings_use_repository_aggregates_and_joined_at_tie_breaker(
    db_session: Session,
) -> None:
    tournament = _create_tournament(db_session)
    owner = _create_user(db_session, "owner-ranking@example.com", "Owner")
    earlier = _create_user(db_session, "earlier@example.com", "Earlier")
    later = _create_user(db_session, "later@example.com", "Later")
    teams = _create_teams(db_session, tournament)
    match_one = _create_match(db_session, tournament, teams[0], teams[1], 1)
    match_two = _create_match(db_session, tournament, teams[2], teams[3], 2)
    db_session.flush()

    pools = PoolsRepository(db_session)
    pool = pools.create_pool(
        tournament_id=tournament.id,
        owner_user_id=owner.id,
        name="Ranking Pool",
        invite_code_hash="ranking-invite-hash",
    )
    earlier_membership = pools.add_participant(pool_id=pool.id, user_id=earlier.id)
    later_membership = pools.add_participant(pool_id=pool.id, user_id=later.id)
    joined_at = datetime(2026, 6, 29, 12, tzinfo=UTC)
    earlier_membership.joined_at = joined_at
    later_membership.joined_at = joined_at + timedelta(minutes=5)

    predictions = PredictionsRepository(db_session)
    earlier_prediction = predictions.upsert_for_user(
        pool_id=pool.id,
        user_id=earlier.id,
        match_id=match_one.id,
        predicted_home_goals=2,
        predicted_away_goals=0,
    )
    later_prediction = predictions.upsert_for_user(
        pool_id=pool.id,
        user_id=later.id,
        match_id=match_two.id,
        predicted_home_goals=2,
        predicted_away_goals=0,
    )
    _add_score(db_session, earlier_prediction, points=4, exact_score=True)
    _add_score(db_session, later_prediction, points=4, exact_score=True)
    db_session.flush()

    service = PredictionService(db_session, Settings(_env_file=None))
    rankings = service.rankings(pool_id=pool.id, user_id=owner.id)

    assert [row[0].id for row in rankings] == [earlier.id, later.id, owner.id]
    assert rankings[0][1:6] == (4, 1, 1, 1, 1)
    assert rankings[1][1:6] == (4, 1, 1, 1, 1)
    assert rankings[2][1:6] == (0, 0, 0, 0, 0)


class PredictionContext:
    def __init__(self, *, pool_id, user: User, match: Match) -> None:
        self.pool_id = pool_id
        self.user = user
        self.match = match


def _create_prediction_context(db_session: Session) -> PredictionContext:
    tournament = _create_tournament(db_session)
    owner = _create_user(db_session, "upsert-owner@example.com", "Owner")
    teams = _create_teams(db_session, tournament)
    match = _create_match(db_session, tournament, teams[0], teams[1], 1)
    db_session.flush()
    pool = PoolsRepository(db_session).create_pool(
        tournament_id=tournament.id,
        owner_user_id=owner.id,
        name="Upsert Pool",
        invite_code_hash="upsert-invite-hash",
    )
    db_session.flush()
    return PredictionContext(pool_id=pool.id, user=owner, match=match)


def _create_tournament(db_session: Session) -> Tournament:
    tournament = Tournament(name=f"World Cup {datetime.now(UTC).timestamp()}", year=2026)
    db_session.add(tournament)
    return tournament


def _create_user(db_session: Session, email: str, display_name: str) -> User:
    user = User(email=email, display_name=display_name, is_active=True)
    db_session.add(user)
    return user


def _create_teams(db_session: Session, tournament: Tournament) -> list[Team]:
    teams = [
        Team(tournament=tournament, name="Spain", short_name="ESP", fifa_code="ESP"),
        Team(tournament=tournament, name="Brazil", short_name="BRA", fifa_code="BRA"),
        Team(tournament=tournament, name="Japan", short_name="JPN", fifa_code="JPN"),
        Team(tournament=tournament, name="Canada", short_name="CAN", fifa_code="CAN"),
    ]
    db_session.add_all(teams)
    return teams


def _create_match(
    db_session: Session,
    tournament: Tournament,
    home_team: Team,
    away_team: Team,
    bracket_position: int,
) -> Match:
    match = Match(
        tournament=tournament,
        stage=TournamentStage.ROUND_OF_32,
        bracket_position=bracket_position,
        home_team=home_team,
        away_team=away_team,
        scheduled_at=datetime(2026, 7, 1, 18, tzinfo=UTC),
        status=MatchStatus.SCHEDULED,
    )
    db_session.add(match)
    return match


def _add_score(
    db_session: Session,
    prediction: Prediction,
    *,
    points: int,
    exact_score: bool,
) -> None:
    db_session.add(
        PredictionScore(
            prediction=prediction,
            points=points,
            correct_winner=True,
            exact_score=exact_score,
            partial_home_goals=False,
            partial_away_goals=False,
            scoring_version="test",
            calculated_at=datetime.now(UTC),
        )
    )
