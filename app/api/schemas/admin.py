from uuid import UUID
from datetime import datetime

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
