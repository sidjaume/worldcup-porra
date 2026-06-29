from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.api.schemas.tournaments import MatchRead
from app.domain.enums import NextSlot, TournamentStage


class CreateMatchRequest(BaseModel):
    stage: TournamentStage
    bracket_position: int = Field(gt=0)
    scheduled_at: datetime
    home_team_id: UUID | None = None
    away_team_id: UUID | None = None
    next_match_id: UUID | None = None
    next_match_slot: NextSlot | None = None


class CompleteMatchRequest(BaseModel):
    home_score: int = Field(ge=0)
    away_score: int = Field(ge=0)
    winner_team_id: UUID


class CompleteMatchResponse(MatchRead):
    pass


class UpdateKickoffRequest(BaseModel):
    """Request body for updating a match kickoff time."""

    scheduled_at: datetime


class SyncTournamentRequest(BaseModel):
    """Request body for running a provider sync."""

    year: int = Field(default=2026, ge=2026)


class SyncResult(BaseModel):
    """Response body for a manual provider sync operation."""

    teams_created: int = 0
    teams_updated: int = 0
    matches_created: int = 0
    matches_updated: int = 0
    errors: list[str] = Field(default_factory=list)
