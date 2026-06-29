"""Fixture sync service.

Provides idempotent operations for importing and synchronising tournament
fixture data from an external provider into the internal domain model.

Design constraints (ARCH-003):
- Business rules (scoring, ranking) remain in the Domain layer.
- Provider data is normalised by the ProviderAdapter before reaching this service.
- Rows with admin_override=True are never overwritten by provider sync.
- Failed provider calls must not corrupt existing data.
- All sync operations are safe to rerun (idempotent).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.enums import MatchStatus
from app.domain.errors import InvalidMatchResultError
from app.domain.services.bracket_progression import BracketProgression, MatchProgression
from app.models.match import Match
from app.models.team import Team
from app.providers.base import ProviderAdapter, ProviderMatch, ProviderTeam
from app.repositories.tournaments import TournamentsRepository
from app.services.errors import ValidationError
from app.services.prediction_service import PredictionService

logger = logging.getLogger(__name__)


@dataclass
class SyncResult:
    """Summary of a single sync operation."""

    teams_created: int = 0
    teams_updated: int = 0
    matches_created: int = 0
    matches_updated: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def total_teams_affected(self) -> int:
        return self.teams_created + self.teams_updated

    @property
    def total_matches_affected(self) -> int:
        return self.matches_created + self.matches_updated

    def merge(self, other: "SyncResult") -> None:
        self.teams_created += other.teams_created
        self.teams_updated += other.teams_updated
        self.matches_created += other.matches_created
        self.matches_updated += other.matches_updated
        self.errors.extend(other.errors)


class FixtureSyncService:
    """Idempotent import and sync operations for tournament fixtures.

    Typical usage:

        adapter = WorldCup2026Adapter()
        svc = FixtureSyncService(db, settings)

        # One-time bracket seed (run from import_fixtures.py)
        result = svc.import_teams(tournament_id, adapter, year=2026)
        result = svc.import_matches(tournament_id, adapter, year=2026)

        # Ongoing operational sync (triggered by admin or scheduler)
        result = svc.sync_results(tournament_id, adapter, year=2026)
    """

    def __init__(self, db: Session, settings) -> None:
        self.db = db
        self.settings = settings
        self.repo = TournamentsRepository(db)
        self._progression = BracketProgression()

    # ------------------------------------------------------------------
    # Public operations
    # ------------------------------------------------------------------

    def import_teams(
        self,
        tournament_id: UUID,
        adapter: ProviderAdapter,
        year: int = 2026,
        *,
        commit: bool = True,
    ) -> SyncResult:
        """Idempotent upsert of teams by provider_ref.

        - Creates teams that do not yet exist.
        - Updates name/short_name/fifa_code/flag_url for existing teams.
        - Never removes teams (safe to rerun).
        """
        result = SyncResult()
        try:
            provider_teams = adapter.fetch_teams(year)
        except Exception as exc:
            msg = f"Provider team fetch failed: {exc}"
            logger.error(msg)
            result.errors.append(msg)
            return result

        for pt in provider_teams:
            try:
                with self.db.begin_nested():
                    self._upsert_team(tournament_id, pt, result)
            except Exception as exc:
                msg = f"Failed to upsert team {pt.provider_ref!r}: {exc}"
                logger.error(msg)
                result.errors.append(msg)

        return self._finalize_sync(result, commit=commit)

    def import_matches(
        self,
        tournament_id: UUID,
        adapter: ProviderAdapter,
        year: int = 2026,
        *,
        commit: bool = True,
    ) -> SyncResult:
        """Idempotent upsert of knockout match fixtures by provider_ref.

        - Creates matches that do not yet exist.
        - Updates scheduled_at, teams, status for existing matches.
        - Never overwrites admin_override rows.
        - Does NOT trigger scoring (call sync_results for that).
        """
        result = SyncResult()
        try:
            provider_matches = adapter.fetch_matches(year)
        except Exception as exc:
            msg = f"Provider match fetch failed: {exc}"
            logger.error(msg)
            result.errors.append(msg)
            return result

        for pm in provider_matches:
            try:
                with self.db.begin_nested():
                    self._upsert_match_fixture(tournament_id, pm, result)
            except Exception as exc:
                msg = f"Failed to upsert match {pm.provider_ref!r}: {exc}"
                logger.error(msg)
                result.errors.append(msg)

        return self._finalize_sync(result, commit=commit)

    def sync_results(
        self,
        tournament_id: UUID,
        adapter: ProviderAdapter,
        year: int = 2026,
        scoring_settings=None,
        *,
        commit: bool = True,
    ) -> SyncResult:
        """Sync completed/in-progress match results from the provider.

        - Skips matches with admin_override=True.
        - Triggers idempotent rescoring via PredictionService for completed matches.
        - Triggers idempotent bracket progression for completed matches.
        - Failed provider calls leave existing data untouched.
        """
        result = SyncResult()
        try:
            provider_matches = adapter.fetch_matches(year)
        except Exception as exc:
            msg = f"Provider match fetch failed during sync: {exc}"
            logger.error(msg)
            result.errors.append(msg)
            return result

        settings = scoring_settings or self.settings
        prediction_service = PredictionService(self.db, settings)

        for pm in provider_matches:
            if pm.status not in (MatchStatus.COMPLETED, MatchStatus.IN_PROGRESS):
                continue
            try:
                with self.db.begin_nested():
                    self._sync_match_result(
                        tournament_id, pm, result, prediction_service
                    )
            except Exception as exc:
                msg = f"Failed to sync result for match {pm.provider_ref!r}: {exc}"
                logger.error(msg)
                result.errors.append(msg)

        return self._finalize_sync(result, commit=commit)

    # ------------------------------------------------------------------
    # Private helpers - team
    # ------------------------------------------------------------------

    def _upsert_team(
        self, tournament_id: UUID, pt: ProviderTeam, result: SyncResult
    ) -> None:
        existing = self.repo.get_team_by_provider_ref(tournament_id, pt.provider_ref)
        if existing is None:
            team = Team(
                tournament_id=tournament_id,
                name=pt.name,
                short_name=pt.short_name,
                fifa_code=pt.fifa_code,
                flag_url=pt.flag_url,
                provider_ref=pt.provider_ref,
            )
            self.db.add(team)
            result.teams_created += 1
            logger.debug("Created team %r (%s)", pt.name, pt.provider_ref)
        else:
            changed = False
            if existing.name != pt.name:
                existing.name = pt.name
                changed = True
            if pt.short_name and existing.short_name != pt.short_name:
                existing.short_name = pt.short_name
                changed = True
            if pt.fifa_code and existing.fifa_code != pt.fifa_code:
                existing.fifa_code = pt.fifa_code
                changed = True
            if pt.flag_url and existing.flag_url != pt.flag_url:
                existing.flag_url = pt.flag_url
                changed = True
            if changed:
                result.teams_updated += 1
                logger.debug("Updated team %r (%s)", pt.name, pt.provider_ref)

    # ------------------------------------------------------------------
    # Private helpers - match fixture
    # ------------------------------------------------------------------

    def _upsert_match_fixture(
        self, tournament_id: UUID, pm: ProviderMatch, result: SyncResult
    ) -> None:
        existing = self.repo.get_match_by_provider_ref(tournament_id, pm.provider_ref)
        if existing is None:
            # Fall back to stage+position lookup (handles pre-seeded bracket)
            existing = self.repo.get_match_by_stage_position(
                tournament_id, pm.stage, pm.bracket_position
            )

        home_team_id = self._resolve_team_id(tournament_id, pm.home_team_provider_ref)
        away_team_id = self._resolve_team_id(tournament_id, pm.away_team_provider_ref)

        if existing is None:
            match = Match(
                tournament_id=tournament_id,
                stage=pm.stage,
                bracket_position=pm.bracket_position,
                scheduled_at=pm.scheduled_at,
                status=pm.status,
                home_team_id=home_team_id,
                away_team_id=away_team_id,
                provider_ref=pm.provider_ref,
                provider_last_synced_at=datetime.now(tz=UTC),
                sync_source="provider",
                admin_override=False,
            )
            self.db.add(match)
            result.matches_created += 1
            logger.debug(
                "Created match %r stage=%s pos=%d",
                pm.provider_ref, pm.stage, pm.bracket_position,
            )
        else:
            if existing.admin_override:
                logger.debug(
                    "Skipping match %s - admin_override is set", existing.id
                )
                return

            changed = False
            # Always update provider_ref binding
            if existing.provider_ref != pm.provider_ref:
                existing.provider_ref = pm.provider_ref
                changed = True
            if existing.scheduled_at != pm.scheduled_at:
                existing.scheduled_at = pm.scheduled_at
                changed = True
            if home_team_id and existing.home_team_id != home_team_id:
                existing.home_team_id = home_team_id
                changed = True
            if away_team_id and existing.away_team_id != away_team_id:
                existing.away_team_id = away_team_id
                changed = True
            if (
                existing.status != pm.status
                and existing.status != MatchStatus.COMPLETED
            ):
                existing.status = pm.status
                changed = True

            existing.provider_last_synced_at = datetime.now(tz=UTC)
            existing.sync_source = "provider"
            if changed:
                result.matches_updated += 1

    # ------------------------------------------------------------------
    # Private helpers - result sync
    # ------------------------------------------------------------------

    def _sync_match_result(
        self,
        tournament_id: UUID,
        pm: ProviderMatch,
        result: SyncResult,
        prediction_service: PredictionService,
    ) -> None:
        match = self.repo.get_match_by_provider_ref(tournament_id, pm.provider_ref)
        if match is None:
            match = self.repo.get_match_by_stage_position(
                tournament_id, pm.stage, pm.bracket_position
            )
        if match is None:
            logger.warning(
                "Cannot sync result for unknown match provider_ref=%r stage=%s pos=%d",
                pm.provider_ref, pm.stage, pm.bracket_position,
            )
            return

        if match.admin_override:
            logger.debug("Skipping result sync for match %s - admin_override", match.id)
            return

        winner_team_id = self._winner_team_id_for_provider_match(tournament_id, pm)
        if pm.status == MatchStatus.COMPLETED:
            self._validate_completed_provider_match(match, pm, winner_team_id)

        changed = False
        if pm.scheduled_at and match.scheduled_at != pm.scheduled_at:
            match.scheduled_at = pm.scheduled_at
            changed = True

        if match.provider_ref != pm.provider_ref:
            match.provider_ref = pm.provider_ref
            changed = True
        if match.status != pm.status:
            match.status = pm.status
            changed = True

        match.provider_last_synced_at = datetime.now(tz=UTC)
        match.sync_source = "provider"

        if pm.status == MatchStatus.COMPLETED:
            if match.home_score != pm.home_score:
                match.home_score = pm.home_score
                changed = True
            if match.away_score != pm.away_score:
                match.away_score = pm.away_score
                changed = True
            if match.winner_team_id != winner_team_id:
                match.winner_team_id = winner_team_id
                changed = True

            prediction_service.score_match_predictions(match)
            self._advance_bracket(match)

        if changed:
            result.matches_updated += 1

    def _winner_team_id_for_provider_match(
        self,
        tournament_id: UUID,
        pm: ProviderMatch,
    ) -> UUID | None:
        if pm.winner_provider_ref is not None:
            return self._resolve_team_id(tournament_id, pm.winner_provider_ref)
        if pm.home_score is None or pm.away_score is None:
            return None
        if pm.home_score > pm.away_score:
            return self._resolve_team_id(tournament_id, pm.home_team_provider_ref)
        if pm.away_score > pm.home_score:
            return self._resolve_team_id(tournament_id, pm.away_team_provider_ref)
        return None

    def _validate_completed_provider_match(
        self,
        match: Match,
        pm: ProviderMatch,
        winner_team_id: UUID | None,
    ) -> None:
        if pm.home_score is None or pm.away_score is None:
            raise ValidationError("Completed provider match must include scores.")
        if pm.home_score < 0 or pm.away_score < 0:
            raise ValidationError("Provider scores must be non-negative.")
        if match.home_team_id is None or match.away_team_id is None:
            raise ValidationError("Completed provider match must have both teams.")
        if winner_team_id not in (match.home_team_id, match.away_team_id):
            raise InvalidMatchResultError(
                "Completed provider match winner must be one of the match teams."
            )
        if pm.home_score == pm.away_score:
            return
        expected = (
            match.home_team_id
            if pm.home_score > pm.away_score
            else match.away_team_id
        )
        if winner_team_id != expected:
            raise InvalidMatchResultError(
                "Completed provider match winner must match the decisive score."
            )

    def _advance_bracket(self, match: Match) -> None:
        try:
            assignment = self._progression.advance(
                MatchProgression(
                    winner_team_id=match.winner_team_id,
                    next_match_id=match.next_match_id,
                    next_match_slot=match.next_match_slot,
                )
            )
        except Exception as exc:
            logger.warning("Bracket progression skipped for match %s: %s", match.id, exc)
            return
        if assignment is None:
            return
        next_match = self.repo.get_match(assignment.next_match_id)
        if next_match is None:
            return
        if assignment.home_team_id is not None:
            next_match.home_team_id = assignment.home_team_id
        if assignment.away_team_id is not None:
            next_match.away_team_id = assignment.away_team_id

    def _finalize_sync(self, result: SyncResult, *, commit: bool) -> SyncResult:
        if result.errors:
            self.db.rollback()
            return result
        if commit:
            try:
                self.db.commit()
            except Exception as exc:
                self.db.rollback()
                msg = f"Database commit failed during sync: {exc}"
                logger.error(msg)
                result.errors.append(msg)
        return result

    def _resolve_team_id(
        self, tournament_id: UUID, provider_ref: str | None
    ) -> UUID | None:
        if provider_ref is None:
            return None
        team = self.repo.get_team_by_provider_ref(tournament_id, provider_ref)
        return team.id if team else None
