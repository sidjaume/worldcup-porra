from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import db_dependency, get_current_user, settings_dependency
from app.api.routers.tournaments import serialize_match
from app.api.schemas.admin import (
    CompleteMatchRequest,
    CreateMatchRequest,
    SyncResult,
    SyncTournamentRequest,
    UpdateKickoffRequest,
    UpdateMatchStatusRequest,
    UpdateMatchTeamsRequest,
)
from app.api.schemas.tournaments import MatchRead
from app.config.settings import Settings
from app.models.user import User
from app.providers.worldcup2026 import WorldCup2026Adapter
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


@router.patch("/matches/{match_id}/kickoff", response_model=MatchRead)
def update_match_kickoff(
    match_id: UUID,
    request: UpdateKickoffRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(db_dependency),
    settings: Settings = Depends(settings_dependency),
) -> MatchRead:
    match = AdminService(db, settings).update_match_kickoff(
        admin_email=current_user.email,
        match_id=match_id,
        scheduled_at=request.scheduled_at,
    )
    return serialize_match(match)


@router.patch("/matches/{match_id}/teams", response_model=MatchRead)
def update_match_teams(
    match_id: UUID,
    request: UpdateMatchTeamsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(db_dependency),
    settings: Settings = Depends(settings_dependency),
) -> MatchRead:
    match = AdminService(db, settings).update_match_teams(
        admin_email=current_user.email,
        match_id=match_id,
        home_team_id=request.home_team_id,
        away_team_id=request.away_team_id,
        update_home_team="home_team_id" in request.model_fields_set,
        update_away_team="away_team_id" in request.model_fields_set,
    )
    return serialize_match(match)


@router.patch("/matches/{match_id}/status", response_model=MatchRead)
def update_match_status(
    match_id: UUID,
    request: UpdateMatchStatusRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(db_dependency),
    settings: Settings = Depends(settings_dependency),
) -> MatchRead:
    match = AdminService(db, settings).update_match_status(
        admin_email=current_user.email,
        match_id=match_id,
        status=request.status,
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


@router.post("/tournaments/{tournament_id}/sync", response_model=SyncResult)
def sync_tournament(
    tournament_id: UUID,
    request: SyncTournamentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(db_dependency),
    settings: Settings = Depends(settings_dependency),
) -> SyncResult:
    adapter = WorldCup2026Adapter(
        base_url=settings.tournament_provider_base_url,
        timeout=settings.tournament_provider_timeout_seconds,
        api_key=settings.tournament_provider_api_key or None,
    )
    result = AdminService(db, settings).sync_provider_data(
        admin_email=current_user.email,
        tournament_id=tournament_id,
        adapter=adapter,
        year=request.year,
    )
    return SyncResult(
        teams_created=result.teams_created,
        teams_updated=result.teams_updated,
        matches_created=result.matches_created,
        matches_updated=result.matches_updated,
        errors=result.errors,
    )
