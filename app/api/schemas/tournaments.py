from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.domain.enums import MatchStatus, TournamentStage


class TournamentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    year: int
    is_active: bool


class TeamRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    short_name: str | None = None
    fifa_code: str | None = None
    flag_url: str | None = None


class TeamBrief(BaseModel):
    id: UUID
    name: str
    short_name: str | None = None
    fifa_code: str | None = None
    flag_url: str | None = None


class MatchRead(BaseModel):
    id: UUID
    stage: TournamentStage
    bracket_position: int
    home_team: TeamBrief | None
    away_team: TeamBrief | None
    scheduled_at: datetime
    status: MatchStatus
    home_score: int | None = None
    away_score: int | None = None
    winner_team_id: UUID | None = None
    live_minute: int | None = None
    # Provider / audit fields (nullable; populated after sync or admin action)
    sync_source: str | None = None
    admin_override: bool = False
    provider_last_synced_at: datetime | None = None
