from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import db_dependency, get_current_user
from app.api.schemas.tournaments import MatchRead, TeamBrief, TeamRead, TournamentRead
from app.domain.enums import MatchStatus, TournamentStage
from app.models.match import Match
from app.models.user import User
from app.services.tournament_service import TournamentService


router = APIRouter(prefix="/tournaments", tags=["tournaments"])


@router.get("", response_model=list[TournamentRead])
def list_tournaments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(db_dependency),
) -> list:
    return TournamentService(db).list_tournaments()


@router.get("/{tournament_id}/teams", response_model=list[TeamRead])
def list_teams(
    tournament_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(db_dependency),
) -> list:
    return TournamentService(db).list_teams(tournament_id)


@router.get("/{tournament_id}/matches", response_model=list[MatchRead])
def list_matches(
    tournament_id: UUID,
    stage: TournamentStage | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(db_dependency),
) -> list[MatchRead]:
    matches = TournamentService(db).list_matches(tournament_id, stage)
    return [serialize_match(match) for match in matches]


def serialize_match(match: Match) -> MatchRead:
    return MatchRead(
        id=match.id,
        stage=match.stage,
        bracket_position=match.bracket_position,
        home_team=(
            TeamBrief(
                id=match.home_team.id,
                name=match.home_team.name,
                short_name=match.home_team.short_name,
                fifa_code=match.home_team.fifa_code,
                flag_url=match.home_team.flag_url,
            )
            if match.home_team
            else None
        ),
        away_team=(
            TeamBrief(
                id=match.away_team.id,
                name=match.away_team.name,
                short_name=match.away_team.short_name,
                fifa_code=match.away_team.fifa_code,
                flag_url=match.away_team.flag_url,
            )
            if match.away_team
            else None
        ),
        scheduled_at=match.scheduled_at,
        status=match.status,
        home_score=match.home_score,
        away_score=match.away_score,
        winner_team_id=match.winner_team_id,
        live_minute=(
            match.live_minute if match.status == MatchStatus.IN_PROGRESS else None
        ),
        sync_source=match.sync_source,
        admin_override=match.admin_override,
        provider_last_synced_at=match.provider_last_synced_at,
    )
