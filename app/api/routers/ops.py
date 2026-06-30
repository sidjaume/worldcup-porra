from secrets import compare_digest
from typing import Annotated

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from app.api.dependencies import db_dependency, settings_dependency
from app.api.schemas.admin import SyncResult as SyncResultResponse
from app.config.settings import Settings
from app.providers.worldcup2026 import WorldCup2026Adapter
from app.services.errors import UnauthorizedError, ValidationError
from app.services.fixture_sync_service import FixtureSyncService, SyncResult


router = APIRouter(prefix="/ops", tags=["ops"])


@router.post("/sync", response_model=SyncResultResponse)
def sync_from_scheduler(
    authorization: Annotated[str | None, Header()] = None,
    db: Session = Depends(db_dependency),
    settings: Settings = Depends(settings_dependency),
) -> SyncResultResponse:
    """Run provider sync from a machine-to-machine scheduler."""

    _require_cron_authorization(authorization, settings)
    if settings.tournament_sync_tournament_id is None:
        raise ValidationError("TOURNAMENT_SYNC_TOURNAMENT_ID is not configured.")

    adapter = WorldCup2026Adapter(
        base_url=settings.tournament_provider_base_url,
        timeout=settings.tournament_provider_timeout_seconds,
        api_key=settings.tournament_provider_api_key or None,
    )
    service = FixtureSyncService(db, settings)
    result = _run_sync_mode(
        service=service,
        tournament_id=settings.tournament_sync_tournament_id,
        adapter=adapter,
        year=settings.tournament_sync_year,
        mode=settings.tournament_sync_mode,
    )
    return SyncResultResponse(
        teams_created=result.teams_created,
        teams_updated=result.teams_updated,
        matches_created=result.matches_created,
        matches_updated=result.matches_updated,
        errors=result.errors,
    )


def _require_cron_authorization(
    authorization: str | None,
    settings: Settings,
) -> None:
    if not settings.cron_secret:
        raise UnauthorizedError("Cron sync is not configured.")
    expected = f"Bearer {settings.cron_secret}"
    if authorization is None or not compare_digest(authorization, expected):
        raise UnauthorizedError("Invalid cron credentials.")


def _run_sync_mode(
    *,
    service: FixtureSyncService,
    tournament_id,
    adapter,
    year: int,
    mode: str,
) -> SyncResult:
    result = SyncResult()
    if mode in ("all", "teams"):
        phase = service.import_teams(tournament_id, adapter, year, commit=False)
        result.merge(phase)
        if phase.errors:
            service.db.rollback()
            return result
    if mode in ("all", "matches"):
        phase = service.import_matches(tournament_id, adapter, year, commit=False)
        result.merge(phase)
        if phase.errors:
            service.db.rollback()
            return result
    if mode in ("all", "results"):
        phase = service.sync_results(tournament_id, adapter, year, commit=False)
        result.merge(phase)
        if phase.errors:
            service.db.rollback()
            return result

    if result.errors:
        service.db.rollback()
    else:
        service.db.commit()
    return result
