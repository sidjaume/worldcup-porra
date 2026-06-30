from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import db_dependency, get_current_user, settings_dependency
from app.api.schemas.predictions import (
    MatchPredictionRead,
    PredictionRead,
    PredictionRequest,
    PredictionScoreRead,
)
from app.config.settings import Settings
from app.domain.enums import TournamentStage
from app.models.prediction import Prediction
from app.models.user import User
from app.services.prediction_service import PredictionService


router = APIRouter(prefix="/pools/{pool_id}", tags=["predictions"])


@router.get("/predictions", response_model=list[PredictionRead])
def list_predictions(
    pool_id: UUID,
    stage: TournamentStage | None = Query(default=None),
    match_id: UUID | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(db_dependency),
    settings: Settings = Depends(settings_dependency),
) -> list[Prediction]:
    return PredictionService(db, settings).list_user_predictions(
        pool_id=pool_id,
        user_id=current_user.id,
        stage=stage,
        match_id=match_id,
    )


@router.put("/matches/{match_id}/prediction", response_model=PredictionRead)
def submit_prediction(
    pool_id: UUID,
    match_id: UUID,
    request: PredictionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(db_dependency),
    settings: Settings = Depends(settings_dependency),
) -> Prediction:
    return PredictionService(db, settings).submit_prediction(
        pool_id=pool_id,
        user_id=current_user.id,
        match_id=match_id,
        predicted_home_goals=request.predicted_home_goals,
        predicted_away_goals=request.predicted_away_goals,
        predicted_winner_team_id=request.predicted_winner_team_id,
    )


@router.get("/matches/{match_id}/predictions", response_model=list[MatchPredictionRead])
def list_match_predictions(
    pool_id: UUID,
    match_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(db_dependency),
    settings: Settings = Depends(settings_dependency),
) -> list[MatchPredictionRead]:
    predictions = PredictionService(db, settings).list_match_predictions(
        pool_id=pool_id,
        user_id=current_user.id,
        match_id=match_id,
    )
    return [
        MatchPredictionRead(
            user_id=prediction.user_id,
            display_name=prediction.user.display_name,
            predicted_home_goals=prediction.predicted_home_goals,
            predicted_away_goals=prediction.predicted_away_goals,
            predicted_winner_team_id=prediction.predicted_winner_team_id,
            submitted_at=prediction.submitted_at,
            score=(
                PredictionScoreRead.model_validate(prediction.score)
                if prediction.score
                else None
            ),
        )
        for prediction in predictions
    ]
