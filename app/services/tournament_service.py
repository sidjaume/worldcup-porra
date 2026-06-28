from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.enums import TournamentStage
from app.repositories.tournaments import TournamentsRepository
from app.services.errors import NotFoundError


class TournamentService:
    def __init__(self, db: Session) -> None:
        self.repo = TournamentsRepository(db)

    def list_tournaments(self):
        return self.repo.list_tournaments()

    def list_teams(self, tournament_id: UUID):
        if self.repo.get_tournament(tournament_id) is None:
            raise NotFoundError("Tournament not found.")
        return self.repo.list_teams(tournament_id)

    def list_matches(self, tournament_id: UUID, stage: TournamentStage | None = None):
        if self.repo.get_tournament(tournament_id) is None:
            raise NotFoundError("Tournament not found.")
        return self.repo.list_matches(tournament_id, stage)

