from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import PoolRole


class PoolCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    tournament_id: UUID


class PoolUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    is_active: bool | None = None


class PoolRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    tournament_id: UUID
    role: PoolRole
    participant_count: int
    created_at: datetime


class PoolCreated(PoolRead):
    invite_code: str


class PoolDetail(BaseModel):
    id: UUID
    name: str
    tournament_id: UUID
    owner_user_id: UUID
    participant_count: int
    created_at: datetime


class JoinPoolRequest(BaseModel):
    invite_code: str = Field(min_length=4, max_length=64)


class JoinPoolResponse(BaseModel):
    pool_id: UUID
    name: str
    role: PoolRole


class RotateInviteCodeResponse(BaseModel):
    invite_code: str
    rotated_at: datetime


class ParticipantRead(BaseModel):
    user_id: UUID
    display_name: str
    role: PoolRole
    joined_at: datetime

