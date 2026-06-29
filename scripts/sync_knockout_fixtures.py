"""Import and sync FIFA World Cup 2026 knockout fixture data.

This script is intentionally thin. Provider normalization lives in
``app.providers`` and persistence/scoring/progression rules live in services.
"""

from __future__ import annotations

import argparse
from uuid import UUID

from app.config.settings import get_settings
from app.db.session import SessionLocal
from app.providers.worldcup2026 import WorldCup2026Adapter
from app.services.fixture_sync_service import FixtureSyncService, SyncResult


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tournament_id", type=UUID)
    parser.add_argument("--year", type=int, default=2026)
    parser.add_argument(
        "--mode",
        choices=("all", "teams", "matches", "results"),
        default="all",
    )
    args = parser.parse_args()

    settings = get_settings()
    adapter = WorldCup2026Adapter(
        base_url=settings.tournament_provider_base_url,
        timeout=settings.tournament_provider_timeout_seconds,
        api_key=settings.tournament_provider_api_key or None,
    )

    with SessionLocal() as db:
        service = FixtureSyncService(db, settings)
        result = SyncResult()
        if args.mode in ("all", "teams"):
            phase = service.import_teams(
                args.tournament_id,
                adapter,
                args.year,
                commit=False,
            )
            result.merge(phase)
            if phase.errors:
                db.rollback()
                print(_format_result(result))
                _print_errors(result)
                return 1
        if args.mode in ("all", "matches"):
            phase = service.import_matches(
                args.tournament_id,
                adapter,
                args.year,
                commit=False,
            )
            result.merge(phase)
            if phase.errors:
                db.rollback()
                print(_format_result(result))
                _print_errors(result)
                return 1
        if args.mode in ("all", "results"):
            phase = service.sync_results(
                args.tournament_id,
                adapter,
                args.year,
                commit=False,
            )
            result.merge(phase)
            if phase.errors:
                db.rollback()
                print(_format_result(result))
                _print_errors(result)
                return 1

        if result.errors:
            db.rollback()
            print(_format_result(result))
            _print_errors(result)
            return 1
        db.commit()

    print(_format_result(result))
    return 0


def _format_result(result: SyncResult) -> str:
    return (
        "teams_created={0} teams_updated={1} matches_created={2} "
        "matches_updated={3} errors={4}".format(
            result.teams_created,
            result.teams_updated,
            result.matches_created,
            result.matches_updated,
            len(result.errors),
        )
    )


def _print_errors(result: SyncResult) -> None:
    for error in result.errors:
        print(f"error: {error}")


if __name__ == "__main__":
    raise SystemExit(main())
