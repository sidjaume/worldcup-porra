from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.entities.scoring import ScoreLine, ScoringConfig
from app.domain.enums import MatchStatus, ParticipantStatus, TournamentStage
from app.domain.errors import PredictionLockedError
from app.domain.services.prediction_policy import PredictionPolicy
from app.domain.services.scoring_engine import ScoringEngine
from app.config.settings import Settings
from app.models.match import Match
from app.repositories.pools import PoolsRepository
from app.repositories.predictions import PredictionsRepository
from app.repositories.tournaments import TournamentsRepository
from app.services.errors import ForbiddenError, NotFoundError, ValidationError


class PredictionService:
    def __init__(self, db: Session, settings: Settings) -> None:
        self.db = db
        self.settings = settings
        self.pools = PoolsRepository(db)
        self.tournaments = TournamentsRepository(db)
        self.predictions = PredictionsRepository(db)
        self.policy = PredictionPolicy()
        self.scoring_engine = ScoringEngine(ScoringConfig(version=settings.scoring_version))

    def submit_prediction(
        self,
        *,
        pool_id: UUID,
        user_id: UUID,
        match_id: UUID,
        predicted_home_goals: int,
        predicted_away_goals: int,
        predicted_winner_team_id: UUID | None = None,
    ):
        pool = self._require_active_participant(pool_id=pool_id, user_id=user_id)
        match = self.tournaments.get_match(match_id)
        if match is None or match.tournament_id != pool.tournament_id:
            raise NotFoundError("Match not found for this pool.")
        if match.home_team_id is None or match.away_team_id is None:
            raise ValidationError("Cannot predict a match before both teams are known.")
        self._validate_predicted_winner(
            match=match,
            predicted_home_goals=predicted_home_goals,
            predicted_away_goals=predicted_away_goals,
            predicted_winner_team_id=predicted_winner_team_id,
        )
        if not self.policy.can_edit(scheduled_at=match.scheduled_at, status=match.status):
            raise PredictionLockedError("Predictions are closed for this match.")

        prediction = self.predictions.upsert_for_user(
            pool_id=pool_id,
            user_id=user_id,
            match_id=match_id,
            predicted_home_goals=predicted_home_goals,
            predicted_away_goals=predicted_away_goals,
            predicted_winner_team_id=predicted_winner_team_id,
        )
        self.db.commit()
        return prediction

    def list_user_predictions(
        self,
        *,
        pool_id: UUID,
        user_id: UUID,
        stage: TournamentStage | None = None,
        match_id: UUID | None = None,
    ):
        self._require_active_participant(pool_id=pool_id, user_id=user_id)
        return self.predictions.list_for_user(
            pool_id=pool_id,
            user_id=user_id,
            stage=stage,
            match_id=match_id,
        )

    def list_match_predictions(self, *, pool_id: UUID, user_id: UUID, match_id: UUID):
        self._require_active_participant(pool_id=pool_id, user_id=user_id)
        match = self.tournaments.get_match(match_id)
        if match is None:
            raise NotFoundError("Match not found.")
        predictions = self.predictions.list_for_match(pool_id=pool_id, match_id=match_id)
        if self.policy.can_edit(scheduled_at=match.scheduled_at, status=match.status):
            return [prediction for prediction in predictions if prediction.user_id == user_id]
        return predictions

    def score_match_predictions(self, match: Match) -> None:
        if match.status != MatchStatus.COMPLETED:
            return
        if match.home_score is None or match.away_score is None:
            raise ValidationError("Completed match must have scores.")
        actual = ScoreLine(
            home_goals=match.home_score,
            away_goals=match.away_score,
            declared_winner_side=self._winner_side_for_match(match),
        )
        for prediction in self.predictions.list_all_for_match(match.id):
            predicted = ScoreLine(
                home_goals=prediction.predicted_home_goals,
                away_goals=prediction.predicted_away_goals,
                declared_winner_side=self._winner_side_for_prediction(prediction, match),
            )
            result = self.scoring_engine.calculate(predicted, actual)
            self.predictions.upsert_score(
                prediction=prediction,
                points=result.points,
                correct_winner=result.correct_winner,
                exact_score=result.exact_score,
                partial_home_goals=result.partial_home_goals,
                partial_away_goals=result.partial_away_goals,
                scoring_version=result.scoring_version,
            )

    @staticmethod
    def _winner_side_for_match(match: Match) -> str | None:
        if match.winner_team_id is None:
            return None
        if match.winner_team_id == match.home_team_id:
            return "home"
        if match.winner_team_id == match.away_team_id:
            return "away"
        raise ValidationError("Match winner must be one of the match teams.")

    @staticmethod
    def _validate_predicted_winner(
        *,
        match: Match,
        predicted_home_goals: int,
        predicted_away_goals: int,
        predicted_winner_team_id: UUID | None,
    ) -> None:
        if predicted_home_goals != predicted_away_goals:
            if predicted_winner_team_id is not None:
                raise ValidationError(
                    "predicted_winner_team_id is only allowed for tied predictions."
                )
            return
        if predicted_winner_team_id is None:
            raise ValidationError(
                "predicted_winner_team_id is required for tied predictions."
            )
        if predicted_winner_team_id not in {match.home_team_id, match.away_team_id}:
            raise ValidationError(
                "predicted_winner_team_id must be one of the match teams."
            )

    @staticmethod
    def _winner_side_for_prediction(prediction, match: Match) -> str | None:
        if prediction.predicted_home_goals != prediction.predicted_away_goals:
            return None
        if prediction.predicted_winner_team_id is None:
            return None
        if prediction.predicted_winner_team_id == match.home_team_id:
            return "home"
        if prediction.predicted_winner_team_id == match.away_team_id:
            return "away"
        raise ValidationError("Predicted winner must be one of the match teams.")

    def rankings(self, *, pool_id: UUID, user_id: UUID):
        self._require_active_participant(pool_id=pool_id, user_id=user_id)
        rows = self.predictions.list_scored_rows(pool_id)
        rows.sort(key=lambda row: (-row[1], -row[2], -row[3], row[6]))
        return rows

    def _require_active_participant(self, *, pool_id: UUID, user_id: UUID):
        pool = self.pools.get(pool_id)
        if pool is None or not pool.is_active:
            raise NotFoundError("Pool not found.")
        participant = self.pools.get_participant(pool_id=pool_id, user_id=user_id)
        if participant is None or participant.status != ParticipantStatus.ACTIVE:
            raise ForbiddenError("You are not a participant in this pool.")
        return pool
