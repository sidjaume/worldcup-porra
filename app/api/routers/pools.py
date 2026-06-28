from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import db_dependency, get_current_user, settings_dependency
from app.api.schemas.pools import (
    JoinPoolRequest,
    JoinPoolResponse,
    ParticipantRead,
    PoolCreate,
    PoolCreated,
    PoolDetail,
    PoolRead,
    PoolUpdate,
    RotateInviteCodeResponse,
)
from app.config.settings import Settings
from app.domain.enums import ParticipantStatus, PoolRole
from app.models.user import User
from app.services.errors import ForbiddenError, NotFoundError, ValidationError
from app.services.pool_service import PoolService


router = APIRouter(prefix="/pools", tags=["pools"])


@router.get("", response_model=list[PoolRead])
def list_pools(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(db_dependency),
    settings: Settings = Depends(settings_dependency),
) -> list[PoolRead]:
    rows = PoolService(db, settings).list_user_pools(current_user.id)
    return [
        PoolRead(
            id=pool.id,
            name=pool.name,
            tournament_id=pool.tournament_id,
            role=role,
            participant_count=count,
            created_at=pool.created_at,
        )
        for pool, role, count in rows
    ]


@router.post("", response_model=PoolCreated, status_code=201)
def create_pool(
    request: PoolCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(db_dependency),
    settings: Settings = Depends(settings_dependency),
) -> PoolCreated:
    pool, invite_code = PoolService(db, settings).create_pool(
        user_id=current_user.id,
        tournament_id=request.tournament_id,
        name=request.name,
    )
    return PoolCreated(
        id=pool.id,
        name=pool.name,
        tournament_id=pool.tournament_id,
        role=PoolRole.OWNER,
        participant_count=1,
        created_at=pool.created_at,
        invite_code=invite_code,
    )


@router.get("/{pool_id}", response_model=PoolDetail)
def get_pool(
    pool_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(db_dependency),
    settings: Settings = Depends(settings_dependency),
) -> PoolDetail:
    service = PoolService(db, settings)
    pool, _participant = service.get_member_pool(
        pool_id=pool_id,
        user_id=current_user.id,
    )
    return PoolDetail(
        id=pool.id,
        name=pool.name,
        tournament_id=pool.tournament_id,
        owner_user_id=pool.owner_user_id,
        participant_count=service.pools.participant_count(pool.id),
        created_at=pool.created_at,
    )


@router.patch("/{pool_id}", response_model=PoolDetail)
def update_pool(
    pool_id: UUID,
    request: PoolUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(db_dependency),
    settings: Settings = Depends(settings_dependency),
) -> PoolDetail:
    service = PoolService(db, settings)
    pool = service.require_owner(pool_id=pool_id, user_id=current_user.id)
    if request.name is not None:
        pool.name = request.name
    if request.is_active is not None:
        pool.is_active = request.is_active
    db.commit()
    db.refresh(pool)
    return PoolDetail(
        id=pool.id,
        name=pool.name,
        tournament_id=pool.tournament_id,
        owner_user_id=pool.owner_user_id,
        participant_count=service.pools.participant_count(pool.id),
        created_at=pool.created_at,
    )


@router.post("/join", response_model=JoinPoolResponse)
def join_pool(
    request: JoinPoolRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(db_dependency),
    settings: Settings = Depends(settings_dependency),
) -> JoinPoolResponse:
    pool, participant = PoolService(db, settings).join_by_invite_code(
        user_id=current_user.id,
        invite_code=request.invite_code,
    )
    return JoinPoolResponse(pool_id=pool.id, name=pool.name, role=participant.role)


@router.get("/{pool_id}/participants", response_model=list[ParticipantRead])
def list_participants(
    pool_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(db_dependency),
    settings: Settings = Depends(settings_dependency),
) -> list[ParticipantRead]:
    participants = PoolService(db, settings).list_participants(
        pool_id=pool_id,
        user_id=current_user.id,
    )
    return [
        ParticipantRead(
            user_id=participant.user_id,
            display_name=participant.user.display_name,
            role=participant.role,
            joined_at=participant.joined_at,
        )
        for participant in participants
    ]


@router.delete("/{pool_id}/participants/{user_id}", status_code=204)
def remove_participant(
    pool_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(db_dependency),
    settings: Settings = Depends(settings_dependency),
) -> None:
    service = PoolService(db, settings)
    pool = service.require_owner(pool_id=pool_id, user_id=current_user.id)
    if pool.owner_user_id == user_id:
        raise ValidationError("Pool owner cannot remove themselves.")
    participant = service.pools.get_participant(pool_id=pool_id, user_id=user_id)
    if participant is None:
        raise NotFoundError("Participant not found.")
    if participant.status != ParticipantStatus.ACTIVE:
        raise ForbiddenError("Participant is already inactive.")
    participant.status = ParticipantStatus.REMOVED
    participant.removed_at = datetime.now(UTC)
    db.commit()


@router.post("/{pool_id}/invite-code/rotate", response_model=RotateInviteCodeResponse)
def rotate_invite_code(
    pool_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(db_dependency),
    settings: Settings = Depends(settings_dependency),
) -> RotateInviteCodeResponse:
    invite_code = PoolService(db, settings).rotate_invite_code(
        pool_id=pool_id,
        user_id=current_user.id,
    )
    return RotateInviteCodeResponse(
        invite_code=invite_code,
        rotated_at=datetime.now(UTC),
    )

