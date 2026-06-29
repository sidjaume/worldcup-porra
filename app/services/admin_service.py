from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.config.settings import Settings
from app.domain.enums import MatchStatus, NextSlot, TournamentStage
from app.domain.errors import InvalidMatchResultError
from app.domain.services.bracket_progression import BracketProgression, MatchProgression
from app.models.match import Match
from app.providers.base import ProviderAdapter
from app.repositories.tournaments import TournamentsRepository
from app.services.errors import ForbiddenError, NotFoundError, ValidationError
from app.services.fixture_sync_service import FixtureSyncService, SyncResult
from app.services.prediction_service import PredictionService


class AdminService:
    def __init__(self, db: Session, settings: Settings) -> None:
        self.db = db
        self.settings = settings
        self.tournaments = TournamentsRepository(db)
        self.progression = BracketProgression()
        self.prediction_service = PredictionService(db, settings)

    def create_match(
        self,
        *,
        admin_email: str,
        tournament_id: UUID,
        stage: TournamentStage,
        bracket_position: int,
        scheduled_at: datetime,
        home_team_id: UUID | None = None,
        away_team_id: UUID | None = None,
        next_match_id: UUID | None = None,
        next_match_slot: NextSlot | None = None,
    ) -> Match:
        self._require_admin(admin_email)
        if self.tournaments.get_tournament(tournament_id) is None:
            raise NotFoundError("Tournament not found.")
        self._validate_team_in_tournament(
            team_id=home_team_id,
            tournament_id=tournament_id,
            label="Home team",
        )
        self._validate_team_in_tournament(
            team_id=away_team_id,
            tournament_id=tournament_id,
            label="Away team",
        )
        self._validate_next_match(
            next_match_id=next_match_id,
            tournament_id=tournament_id,
        )
        if next_match_id is not None and next_match_slot is None:
            raise ValidationError("Next match slot is required when next match is set.")
        if (
            home_team_id is not None
            and away_team_id is not None
            and home_team_id == away_team_id
        ):
            raise ValidationError("Home and away teams must be different.")
        match = Match(
            tournament_id=tournament_id,
            stage=stage,
            bracket_position=bracket_position,
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            scheduled_at=scheduled_at,
            status=MatchStatus.SCHEDULED,
            next_match_id=next_match_id,
            next_match_slot=next_match_slot,
            sync_source="admin",
        )
        self.db.add(match)
        self.db.commit()
        self.db.refresh(match)
        return match

    def complete_match(
        self,
        *,
        admin_email: str,
        match_id: UUID,
        home_score: int,
        away_score: int,
        winner_team_id: UUID,
    ):
        self._require_admin(admin_email)
        match = self.tournaments.get_match(match_id)
        if match is None:
            raise NotFoundError("Match not found.")
        if home_score < 0 or away_score < 0:
            raise ValidationError("Scores must be non-negative.")
        if match.home_team_id is None or match.away_team_id is None:
            raise ValidationError("Match teams must be known before completion.")
        self._validate_winner(
            home_team_id=match.home_team_id,
            away_team_id=match.away_team_id,
            home_score=home_score,
            away_score=away_score,
            winner_team_id=winner_team_id,
        )

        match.home_score = home_score
        match.away_score = away_score
        match.winner_team_id = winner_team_id
        match.status = MatchStatus.COMPLETED
        match.sync_source = "admin"
        match.admin_override = True

        assignment = self.progression.advance(
            MatchProgression(
                winner_team_id=winner_team_id,
                next_match_id=match.next_match_id,
                next_match_slot=match.next_match_slot,
            )
        )
        if assignment is not None:
            next_match = self.tournaments.get_match(assignment.next_match_id)
            if next_match is None:
                raise ValidationError("Configured next match was not found.")
            if assignment.home_team_id is not None:
                next_match.home_team_id = assignment.home_team_id
            if assignment.away_team_id is not None:
                next_match.away_team_id = assignment.away_team_id

        self.prediction_service.score_match_predictions(match)
        self.db.commit()
        return match

    def rescore_match(self, *, admin_email: str, match_id: UUID) -> Match:
        self._require_admin(admin_email)
        match = self.tournaments.get_match(match_id)
        if match is None:
            raise NotFoundError("Match not found.")
        if match.status != MatchStatus.COMPLETED:
            raise ValidationError("Only completed matches can be rescored.")
        self.prediction_service.score_match_predictions(match)
        self.db.commit()
        return match

    def update_match_kickoff(
        self,
        *,
        admin_email: str,
        match_id: UUID,
        scheduled_at: datetime,
    ) -> Match:
        """Update a match's kickoff time.

        Sets admin_override=True to prevent provider sync from silently
        undoing the correction.  Prediction-lock policy uses scheduled_at, so
        changing the kickoff here will affect whether predictions are still editable.
        """
        self._require_admin(admin_email)
        match = self.tournaments.get_match(match_id)
        if match is None:
            raise NotFoundError("Match not found.")
        if match.status == MatchStatus.COMPLETED:
            raise ValidationError("Cannot change kickoff time of a completed match.")
        match.scheduled_at = scheduled_at
        match.sync_source = "admin"
        match.admin_override = True
        self.db.commit()
        return match

    def sync_provider_data(
        self,
        *,
        admin_email: str,
        tournament_id: UUID,
        adapter: ProviderAdapter,
        year: int = 2026,
    ) -> SyncResult:
        self._require_admin(admin_email)
        if self.tournaments.get_tournament(tournament_id) is None:
            raise NotFoundError("Tournament not found.")

        fixture_sync = FixtureSyncService(self.db, self.settings)
        result = SyncResult()
        phase = fixture_sync.import_teams(tournament_id, adapter, year, commit=False)
        result.merge(phase)
        if phase.errors:
            self.db.rollback()
            return result

        phase = fixture_sync.import_matches(
            tournament_id,
            adapter,
            year,
            commit=False,
        )
        result.merge(phase)
        if phase.errors:
            self.db.rollback()
            return result

        phase = fixture_sync.sync_results(tournament_id, adapter, year, commit=False)
        result.merge(phase)
        if phase.errors:
            self.db.rollback()
            return result

        self.db.commit()
        return result

    def _require_admin(self, email: str) -> None:
        allowed = {item.lower() for item in self.settings.admin_emails}
        if email.lower() not in allowed:
            raise ForbiddenError("Admin access is required.")

    def _validate_team_in_tournament(
        self,
        *,
        team_id: UUID | None,
        tournament_id: UUID,
        label: str,
    ) -> None:
        if team_id is None:
            return
        team = self.tournaments.get_team(team_id)
        if team is None:
            raise NotFoundError(f"{label} not found.")
        if team.tournament_id != tournament_id:
            raise ValidationError(f"{label} does not belong to this tournament.")

    def _validate_next_match(
        self,
        *,
        next_match_id: UUID | None,
        tournament_id: UUID,
    ) -> None:
        if next_match_id is None:
            return
        next_match = self.tournaments.get_match(next_match_id)
        if next_match is None:
            raise NotFoundError("Next match not found.")
        if next_match.tournament_id != tournament_id:
            raise ValidationError("Next match does not belong to this tournament.")

    @staticmethod
    def _validate_winner(
        *,
        home_team_id: UUID,
        away_team_id: UUID,
        home_score: int,
        away_score: int,
        winner_team_id: UUID,
    ) -> None:
        """Validate that the declared winner is consistent with the score.

        ARCH-003 allows tied end-of-play scores (penalty-decided matches).
        In that case, the winner_team_id must still be one of the two teams.
        If the score is decisive (one side has more goals) the winner must
        match the higher-scoring side.
        """
        if winner_team_id not in (home_team_id, away_team_id):
            raise InvalidMatchResultError(
                "Winner must be one of the two teams in this match."
            )
        if home_score == away_score:
            # Tied end-of-play score is valid (penalty-decided match).
            # The caller declares the advancing team explicitly.
            return
        expected = home_team_id if home_score > away_score else away_team_id
        if expected != winner_team_id:
            raise InvalidMatchResultError(
                "Winner must match the higher-scoring team."
            )
