from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.domain.enums import TournamentStage
from app.models.match import Match
from app.models.team import Team
from app.models.tournament import Tournament


class TournamentsRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_tournaments(self) -> list[Tournament]:
        return list(self.db.scalars(select(Tournament).order_by(Tournament.year.desc())))

    def get_tournament(self, tournament_id: UUID) -> Tournament | None:
        return self.db.get(Tournament, tournament_id)

    def list_teams(self, tournament_id: UUID) -> list[Team]:
        return list(
            self.db.scalars(
                select(Team)
                .where(Team.tournament_id == tournament_id)
                .order_by(Team.name.asc())
            )
        )

    def get_team(self, team_id: UUID) -> Team | None:
        return self.db.get(Team, team_id)

    def list_matches(
        self,
        tournament_id: UUID,
        stage: TournamentStage | None = None,
    ) -> list[Match]:
        query = (
            select(Match)
            .options(
                selectinload(Match.home_team),
                selectinload(Match.away_team),
                selectinload(Match.winner_team),
            )
            .where(Match.tournament_id == tournament_id)
            .order_by(Match.stage.asc(), Match.bracket_position.asc())
        )
        if stage is not None:
            query = query.where(Match.stage == stage)
        return list(self.db.scalars(query))

    def get_match(self, match_id: UUID) -> Match | None:
        return self.db.scalar(
            select(Match)
            .options(
                selectinload(Match.home_team),
                selectinload(Match.away_team),
                selectinload(Match.winner_team),
            )
            .where(Match.id == match_id)
        )
