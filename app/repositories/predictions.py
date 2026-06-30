from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import Integer, func, select
from sqlalchemy.orm import Session, selectinload

from app.domain.enums import ParticipantStatus, PredictionStatus, TournamentStage
from app.models.match import Match
from app.models.pool import PoolParticipant
from app.models.prediction import Prediction, PredictionScore
from app.models.user import User

RankingRow = tuple[User, int, int, int, int, int, datetime]


class PredictionsRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_for_user(
        self,
        *,
        pool_id: UUID,
        user_id: UUID,
        match_id: UUID,
    ) -> Prediction | None:
        return self.db.scalar(
            select(Prediction).where(
                Prediction.pool_id == pool_id,
                Prediction.user_id == user_id,
                Prediction.match_id == match_id,
            )
        )

    def upsert_for_user(
        self,
        *,
        pool_id: UUID,
        user_id: UUID,
        match_id: UUID,
        predicted_home_goals: int,
        predicted_away_goals: int,
        predicted_winner_team_id: UUID | None = None,
    ) -> Prediction:
        now = datetime.now(UTC)
        prediction = self.get_for_user(
            pool_id=pool_id,
            user_id=user_id,
            match_id=match_id,
        )
        if prediction is None:
            prediction = Prediction(
                pool_id=pool_id,
                user_id=user_id,
                match_id=match_id,
                predicted_home_goals=predicted_home_goals,
                predicted_away_goals=predicted_away_goals,
                predicted_winner_team_id=predicted_winner_team_id,
                status=PredictionStatus.EDITABLE,
                submitted_at=now,
                updated_at=now,
            )
            self.db.add(prediction)
        else:
            prediction.predicted_home_goals = predicted_home_goals
            prediction.predicted_away_goals = predicted_away_goals
            prediction.predicted_winner_team_id = predicted_winner_team_id
            prediction.status = PredictionStatus.EDITABLE
            prediction.updated_at = now
        self.db.flush()
        return prediction

    def list_for_user(
        self,
        *,
        pool_id: UUID,
        user_id: UUID,
        stage: TournamentStage | None = None,
        match_id: UUID | None = None,
    ) -> list[Prediction]:
        query = (
            select(Prediction)
            .join(Match)
            .options(selectinload(Prediction.score))
            .where(Prediction.pool_id == pool_id, Prediction.user_id == user_id)
            .order_by(Match.stage.asc(), Match.bracket_position.asc())
        )
        if stage is not None:
            query = query.where(Match.stage == stage)
        if match_id is not None:
            query = query.where(Prediction.match_id == match_id)
        return list(self.db.scalars(query))

    def list_for_match(self, *, pool_id: UUID, match_id: UUID) -> list[Prediction]:
        return list(
            self.db.scalars(
                select(Prediction)
                .options(
                    selectinload(Prediction.user),
                    selectinload(Prediction.score),
                )
                .where(Prediction.pool_id == pool_id, Prediction.match_id == match_id)
                .order_by(Prediction.submitted_at.asc())
            )
        )

    def list_all_for_match(self, match_id: UUID) -> list[Prediction]:
        return list(
            self.db.scalars(
                select(Prediction)
                .options(selectinload(Prediction.score))
                .where(Prediction.match_id == match_id)
                .order_by(Prediction.submitted_at.asc())
            )
        )

    def list_scored_rows(
        self,
        pool_id: UUID,
    ) -> list[RankingRow]:
        rows = self.db.execute(
            select(
                User,
                func.coalesce(func.sum(PredictionScore.points), 0).label("total_points"),
                func.coalesce(
                    func.sum(PredictionScore.exact_score.cast(Integer)),
                    0,
                ).label("exact_scores"),
                func.coalesce(
                    func.sum(PredictionScore.correct_winner.cast(Integer)),
                    0,
                ).label("correct_winners"),
                func.count(PredictionScore.id).label("predictions_scored"),
                func.count(Prediction.id).label("predictions_submitted"),
                PoolParticipant.joined_at,
            )
            .join(PoolParticipant, PoolParticipant.user_id == User.id)
            .outerjoin(
                Prediction,
                (Prediction.user_id == User.id) & (Prediction.pool_id == pool_id),
            )
            .outerjoin(PredictionScore, PredictionScore.prediction_id == Prediction.id)
            .where(PoolParticipant.pool_id == pool_id)
            .where(PoolParticipant.status == ParticipantStatus.ACTIVE)
            .group_by(User.id, PoolParticipant.joined_at)
        )
        return [
            (
                user,
                int(total_points or 0),
                int(exact_scores or 0),
                int(correct_winners or 0),
                int(predictions_scored or 0),
                int(predictions_submitted or 0),
                joined_at,
            )
            for (
                user,
                total_points,
                exact_scores,
                correct_winners,
                predictions_scored,
                predictions_submitted,
                joined_at,
            ) in rows
        ]

    def upsert_score(
        self,
        *,
        prediction: Prediction,
        points: int,
        correct_winner: bool,
        exact_score: bool,
        partial_home_goals: bool,
        partial_away_goals: bool,
        scoring_version: str,
    ) -> PredictionScore:
        now = datetime.now(UTC)
        score = prediction.score or self.db.scalar(
            select(PredictionScore).where(
                PredictionScore.prediction_id == prediction.id,
            )
        )
        if score is None:
            score = PredictionScore(
                prediction_id=prediction.id,
                points=points,
                correct_winner=correct_winner,
                exact_score=exact_score,
                partial_home_goals=partial_home_goals,
                partial_away_goals=partial_away_goals,
                scoring_version=scoring_version,
                calculated_at=now,
            )
            self.db.add(score)
            prediction.score = score
        else:
            score.points = points
            score.correct_winner = correct_winner
            score.exact_score = exact_score
            score.partial_home_goals = partial_home_goals
            score.partial_away_goals = partial_away_goals
            score.scoring_version = scoring_version
            score.calculated_at = now
        prediction.status = PredictionStatus.SCORED
        self.db.flush()
        return score
