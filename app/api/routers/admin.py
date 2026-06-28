from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import db_dependency, get_current_user, settings_dependency
from app.api.routers.tournaments import serialize_match
from app.api.schemas.admin import CompleteMatchRequest, CreateMatchRequest
from app.api.schemas.tournaments import MatchRead
from app.config.settings import Settings
from app.models.user import User
from app.services.admin_service import AdminService


router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/tournaments/{tournament_id}/matches", response_model=MatchRead, status_code=201)
def create_match(
    tournament_id: UUID,
    request: CreateMatchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(db_dependency),
    settings: Settings = Depends(settings_dependency),
) -> MatchRead:
    match = AdminService(db, settings).create_match(
        admin_email=current_user.email,
        tournament_id=tournament_id,
        stage=request.stage,
        bracket_position=request.bracket_position,
        scheduled_at=request.scheduled_at,
        home_team_id=request.home_team_id,
        away_team_id=request.away_team_id,
        next_match_id=request.next_match_id,
        next_match_slot=request.next_match_slot,
    )
    return serialize_match(match)


@router.patch("/matches/{match_id}", response_model=MatchRead)
def complete_match(
    match_id: UUID,
    request: CompleteMatchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(db_dependency),
    settings: Settings = Depends(settings_dependency),
) -> MatchRead:
    match = AdminService(db, settings).complete_match(
        admin_email=current_user.email,
        match_id=match_id,
        home_score=request.home_score,
        away_score=request.away_score,
        winner_team_id=request.winner_team_id,
    )
    return serialize_match(match)


@router.post("/matches/{match_id}/rescore", response_model=MatchRead)
def rescore_match(
    match_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(db_dependency),
    settings: Settings = Depends(settings_dependency),
) -> MatchRead:
    match = AdminService(db, settings).rescore_match(
        admin_email=current_user.email,
        match_id=match_id,
    )
    return serialize_match(match)
