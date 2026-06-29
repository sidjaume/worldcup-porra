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

    def get_team_by_provider_ref(
        self, tournament_id: UUID, provider_ref: str
    ) -> Team | None:
        """Look up a team by its external provider reference ID."""
        return self.db.scalar(
            select(Team)
            .where(
                Team.tournament_id == tournament_id,
                Team.provider_ref == provider_ref,
            )
        )

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

    def get_match_by_provider_ref(
        self, tournament_id: UUID, provider_ref: str
    ) -> Match | None:
        """Look up a match by its external provider reference ID."""
        return self.db.scalar(
            select(Match)
            .options(
                selectinload(Match.home_team),
                selectinload(Match.away_team),
                selectinload(Match.winner_team),
            )
            .where(
                Match.tournament_id == tournament_id,
                Match.provider_ref == provider_ref,
            )
        )

    def get_match_by_stage_position(
        self,
        tournament_id: UUID,
        stage: TournamentStage,
        bracket_position: int,
    ) -> Match | None:
        """Look up a match by its canonical stage and bracket position.

        Used as a fallback when provider_ref is not yet stored on an existing
        pre-seeded match (e.g. first import run after admin-seeded bracket).
        """
        return self.db.scalar(
            select(Match)
            .options(
                selectinload(Match.home_team),
                selectinload(Match.away_team),
                selectinload(Match.winner_team),
            )
            .where(
                Match.tournament_id == tournament_id,
                Match.stage == stage,
                Match.bracket_position == bracket_position,
            )
        )

    def list_completed_matches_for_rescore(
        self, tournament_id: UUID
    ) -> list[Match]:
        """Return all completed matches for a tournament, ordered by stage and position.

        Used by sync to identify matches that need rescoring after a correction.
        """
        from app.domain.enums import MatchStatus

        return list(
            self.db.scalars(
                select(Match)
                .options(
                    selectinload(Match.home_team),
                    selectinload(Match.away_team),
                    selectinload(Match.winner_team),
                )
                .where(
                    Match.tournament_id == tournament_id,
                    Match.status == MatchStatus.COMPLETED,
                )
                .order_by(Match.stage.asc(), Match.bracket_position.asc())
            )
        )
