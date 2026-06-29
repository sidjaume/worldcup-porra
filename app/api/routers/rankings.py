from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import db_dependency, get_current_user, settings_dependency
from app.api.schemas.predictions import RankingRead
from app.config.settings import Settings
from app.models.user import User
from app.services.prediction_service import PredictionService


router = APIRouter(prefix="/pools/{pool_id}/rankings", tags=["rankings"])


@router.get("", response_model=list[RankingRead])
def rankings(
    pool_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(db_dependency),
    settings: Settings = Depends(settings_dependency),
) -> list[RankingRead]:
    rows = PredictionService(db, settings).rankings(pool_id=pool_id, user_id=current_user.id)
    return [
        RankingRead(
            rank=index,
            user_id=user.id,
            display_name=user.display_name,
            total_points=total_points,
            exact_scores=exact_scores,
            correct_winners=correct_winners,
            predictions_scored=predictions_scored,
            predictions_submitted=predictions_submitted,
        )
        for index, (
            user,
            total_points,
            exact_scores,
            correct_winners,
            predictions_scored,
            predictions_submitted,
            _joined_at,
        ) in enumerate(rows, start=1)
    ]
