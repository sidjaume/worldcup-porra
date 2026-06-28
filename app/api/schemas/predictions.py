from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import PredictionStatus


class PredictionRequest(BaseModel):
    predicted_home_goals: int = Field(ge=0)
    predicted_away_goals: int = Field(ge=0)


class PredictionScoreRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    points: int
    correct_winner: bool
    exact_score: bool
    partial_home_goals: bool
    partial_away_goals: bool
    scoring_version: str


class PredictionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    pool_id: UUID
    match_id: UUID
    predicted_home_goals: int
    predicted_away_goals: int
    status: PredictionStatus
    submitted_at: datetime
    updated_at: datetime
    score: PredictionScoreRead | None = None


class MatchPredictionRead(BaseModel):
    user_id: UUID
    display_name: str
    predicted_home_goals: int
    predicted_away_goals: int
    submitted_at: datetime
    score: PredictionScoreRead | None = None


class RankingRead(BaseModel):
    rank: int
    user_id: UUID
    display_name: str
    total_points: int
    exact_scores: int
    correct_winners: int
    predictions_scored: int
    predictions_submitted: int

