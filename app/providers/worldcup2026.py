"""WorldCup2026 provider adapter.

Reads knockout fixture data from the ``rezarahiminia/worldcup2026`` open-source
project (https://github.com/rezarahiminia/worldcup2026).

Data source strategy (ARCH-003):
- Primary: fetch JSON from the provider's public REST API.
- The adapter filters to the knockout rounds supported by this application.
- If the remote endpoint is unavailable, callers receive a ProviderError so
  the sync service can handle the failure without corrupting existing data.

Normalisation rules:
- Provider status values are mapped to internal MatchStatus enum values.
- Provider stage names are mapped to internal TournamentStage enum values.
- Only knockout stages are returned; all group-stage entries are discarded.
- End-of-play scores are used; penalty shoot-out goals are never added.
- A winner_provider_ref is set if the provider reports a winner, even when
  the end-of-play score is tied (penalty-decided match).
"""

from __future__ import annotations

import json
import logging
import urllib.request
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

from app.domain.enums import MatchStatus, TournamentStage
from app.providers.base import ProviderMatch, ProviderTeam

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Public API base URL for rezarahiminia/worldcup2026
# ---------------------------------------------------------------------------
_DEFAULT_BASE_URL = "https://worldcup26.ir/get"

# Mapping from provider stage strings to internal TournamentStage values.
# The provider may use different casing or formatting; all comparisons are
# performed after .lower().strip().
_STAGE_MAP: dict[str, TournamentStage] = {
    "round of 32": TournamentStage.ROUND_OF_32,
    "round_of_32": TournamentStage.ROUND_OF_32,
    "r32": TournamentStage.ROUND_OF_32,
    "round of 16": TournamentStage.ROUND_OF_16,
    "round_of_16": TournamentStage.ROUND_OF_16,
    "r16": TournamentStage.ROUND_OF_16,
    "quarterfinal": TournamentStage.QUARTER_FINAL,
    "quarter-final": TournamentStage.QUARTER_FINAL,
    "quarter_final": TournamentStage.QUARTER_FINAL,
    "quarterfinals": TournamentStage.QUARTER_FINAL,
    "quarter-finals": TournamentStage.QUARTER_FINAL,
    "qf": TournamentStage.QUARTER_FINAL,
    "semifinal": TournamentStage.SEMI_FINAL,
    "semi-final": TournamentStage.SEMI_FINAL,
    "semi_final": TournamentStage.SEMI_FINAL,
    "semifinals": TournamentStage.SEMI_FINAL,
    "semi-finals": TournamentStage.SEMI_FINAL,
    "sf": TournamentStage.SEMI_FINAL,
    "final": TournamentStage.FINAL,
    "finals": TournamentStage.FINAL,
}

# Mapping from provider status strings to internal MatchStatus values.
_STATUS_MAP: dict[str, MatchStatus] = {
    "upcoming": MatchStatus.SCHEDULED,
    "scheduled": MatchStatus.SCHEDULED,
    "tbd": MatchStatus.SCHEDULED,
    "not started": MatchStatus.SCHEDULED,
    "live": MatchStatus.IN_PROGRESS,
    "in_progress": MatchStatus.IN_PROGRESS,
    "in progress": MatchStatus.IN_PROGRESS,
    "halftime": MatchStatus.IN_PROGRESS,
    "half-time": MatchStatus.IN_PROGRESS,
    "extra time": MatchStatus.IN_PROGRESS,
    "penalties": MatchStatus.IN_PROGRESS,
    "finished": MatchStatus.COMPLETED,
    "completed": MatchStatus.COMPLETED,
    "full-time": MatchStatus.COMPLETED,
    "fulltime": MatchStatus.COMPLETED,
    "ft": MatchStatus.COMPLETED,
    "aet": MatchStatus.COMPLETED,
    "pen": MatchStatus.COMPLETED,
    "cancelled": MatchStatus.CANCELLED,
    "postponed": MatchStatus.CANCELLED,
}

_KNOCKOUT_STAGES = set(TournamentStage)


class ProviderError(Exception):
    """Raised when the provider is unreachable or returns unexpected data."""


class WorldCup2026Adapter:
    """Adapter for the rezarahiminia/worldcup2026 data source.

    The adapter can be constructed with an optional ``base_url`` override for
    testing or self-hosted deployments.  The ``timeout`` parameter controls the
    HTTP request timeout in seconds (default 10).
    """

    def __init__(
        self,
        base_url: str = _DEFAULT_BASE_URL,
        timeout: int = 10,
        api_key: str | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._api_key = api_key

    # ------------------------------------------------------------------
    # ProviderAdapter protocol
    # ------------------------------------------------------------------

    def fetch_teams(self, tournament_year: int) -> list[ProviderTeam]:  # noqa: ARG002
        """Fetch the teams that participate in the knockout subset only."""
        knockout_team_refs = self._knockout_team_refs()
        raw = self._get("/teams")
        teams: list[ProviderTeam] = []
        for item in raw:
            if not isinstance(item, dict):
                continue
            team = self._normalise_team(item)
            if team is not None and team.provider_ref in knockout_team_refs:
                teams.append(team)
        return teams

    def fetch_matches(self, tournament_year: int) -> list[ProviderMatch]:  # noqa: ARG002
        """Fetch matches from the provider and return only knockout-stage records."""
        raw = sorted(self._get("/games"), key=self._sort_key)
        matches: list[ProviderMatch] = []
        stage_counts: dict[TournamentStage, int] = {}
        for item in raw:
            if not isinstance(item, dict):
                continue
            stage = self._parse_stage(item)
            if stage is None:
                continue
            stage_counts[stage] = stage_counts.get(stage, 0) + 1
            match = self._normalise_match(
                item=item,
                stage=stage,
                fallback_bracket_position=stage_counts[stage],
            )
            if match is not None:
                matches.append(match)
        return matches

    # ------------------------------------------------------------------
    # HTTP helpers
    # ------------------------------------------------------------------

    def _get(self, path: str) -> list[Any]:
        url = f"{self._base_url}{path}"
        headers: dict[str, str] = {"Accept": "application/json"}
        if self._api_key:
            headers["x-rapidapi-key"] = self._api_key
            headers["x-rapidapi-host"] = urlparse(self._base_url).netloc
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=self._timeout) as response:
                body = response.read().decode("utf-8")
                data = json.loads(body)
                # Provider may return {"data": [...]} or directly [...]
                if isinstance(data, list):
                    return data
                if isinstance(data, dict):
                    for key in ("data", "matches", "teams", "results"):
                        if isinstance(data.get(key), list):
                            return data[key]
                raise ProviderError(
                    f"Unexpected provider response structure from {url}"
                )
        except Exception as exc:
            raise ProviderError(f"Failed to fetch {url}: {exc}") from exc

    # ------------------------------------------------------------------
    # Normalisation helpers
    # ------------------------------------------------------------------

    def _normalise_team(self, item: dict[str, Any]) -> ProviderTeam | None:
        ref = self._first_present(item, "id", "_id", "team_id")
        name = self._first_present(item, "name", "name_en", "team_name", "team")
        if ref is None or name is None:
            raise ProviderError(f"Provider team missing ref/name: {item}")
        return ProviderTeam(
            provider_ref=str(ref),
            name=str(name),
            short_name=item.get("short_name") or item.get("code") or item.get("fifa_code"),
            fifa_code=item.get("fifa_code") or item.get("code"),
            flag_url=item.get("flag") or item.get("flag_url"),
        )

    def _normalise_match(
        self,
        *,
        item: dict[str, Any],
        stage: TournamentStage,
        fallback_bracket_position: int,
    ) -> ProviderMatch | None:
        ref = self._first_present(item, "id", "_id", "match_id", "match_number")
        if ref is None:
            raise ProviderError(f"Provider match missing ID field: {item}")

        bracket_position = self._safe_int(
            self._first_present(item, "bracket_position", "position")
        )
        if bracket_position is None:
            bracket_position = fallback_bracket_position

        scheduled_at = self._parse_datetime(
            self._first_present(
                item,
                "date",
                "datetime",
                "scheduled_at",
                "kickoff",
                "kickoff_at",
            )
        )
        if scheduled_at is None:
            raise ProviderError(f"Provider match {ref} has no parseable date.")

        status_raw = str(
            item.get("status") or item.get("match_status") or "scheduled"
        ).lower().strip()
        status = _STATUS_MAP.get(status_raw, MatchStatus.SCHEDULED)

        home_team_ref = self._team_ref(item, "home")
        away_team_ref = self._team_ref(item, "away")

        home_score: int | None = None
        away_score: int | None = None
        winner_ref: str | None = None

        if status == MatchStatus.COMPLETED:
            score_data = item.get("score") or item
            home_score = self._safe_int(
                score_data.get("home_score")
                or score_data.get("home_goals")
                or item.get("home_score")
            )
            away_score = self._safe_int(
                score_data.get("away_score")
                or score_data.get("away_goals")
                or item.get("away_score")
            )
            if home_score is None or away_score is None:
                raise ProviderError(
                    f"Provider match {ref} is completed but missing scores."
                )
            winner_ref = self._extract_winner_ref(item)

        return ProviderMatch(
            provider_ref=str(ref),
            stage=stage,
            bracket_position=bracket_position,
            scheduled_at=scheduled_at,
            status=status,
            home_team_provider_ref=home_team_ref,
            away_team_provider_ref=away_team_ref,
            home_score=home_score,
            away_score=away_score,
            winner_provider_ref=winner_ref,
        )

    # ------------------------------------------------------------------
    # Field parsers
    # ------------------------------------------------------------------

    def _parse_stage(self, item: dict[str, Any]) -> TournamentStage | None:
        stage_raw = str(
            item.get("stage")
            or item.get("round")
            or item.get("phase")
            or item.get("type")
            or item.get("match_type")
            or ""
        ).lower().strip()
        return _STAGE_MAP.get(stage_raw)

    @staticmethod
    def _parse_datetime(value: Any) -> datetime | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
        raw = str(value).strip()
        if not raw:
            return None
        # Try ISO 8601 first (most common in modern APIs)
        for fmt in (
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
        ):
            try:
                dt = datetime.strptime(raw, fmt)
                return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
            except ValueError:
                continue
        logger.warning("Could not parse provider datetime: %r", raw)
        return None

    @staticmethod
    def _safe_int(value: Any) -> int | None:
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _team_ref(item: dict[str, Any], side: str) -> str | None:
        """Extract team provider_ref for the given side ('home' or 'away')."""
        # Try nested dict first: {"home_team": {"id": ...}}
        nested = item.get(f"{side}_team")
        if isinstance(nested, dict):
            ref = nested.get("id") or nested.get("team_id")
            if ref is not None:
                return str(ref)
        # Flat field: home_team_id, away_team_id
        flat = item.get(f"{side}_team_id")
        if flat is not None:
            return str(flat)
        camel = item.get(f"{side}Team")
        if isinstance(camel, dict):
            ref = camel.get("id") or camel.get("_id") or camel.get("team_id")
            if ref is not None:
                return str(ref)
        camel_id = item.get(f"{side}TeamId")
        if camel_id is not None:
            return str(camel_id)
        return None

    @staticmethod
    def _extract_winner_ref(item: dict[str, Any]) -> str | None:
        """Extract the advancing team provider_ref from the match record."""
        # Try nested winner object
        winner = item.get("winner")
        if isinstance(winner, dict):
            ref = winner.get("id") or winner.get("team_id")
            if ref is not None:
                return str(ref)
        # Flat field
        flat = item.get("winner_team_id") or item.get("winner_id")
        if flat is not None:
            return str(flat)
        return None

    @staticmethod
    def _first_present(item: dict[str, Any], *keys: str) -> Any:
        for key in keys:
            value = item.get(key)
            if value not in (None, ""):
                return value
        return None

    @staticmethod
    def _sort_key(item: Any) -> tuple[int, str]:
        if not isinstance(item, dict):
            return (9999, "")
        raw = (
            item.get("match_number")
            or item.get("game_number")
            or item.get("id")
            or item.get("_id")
            or 9999
        )
        try:
            return (int(raw), str(raw))
        except (TypeError, ValueError):
            return (9999, str(raw))

    def _knockout_team_refs(self) -> set[str]:
        refs: set[str] = set()
        for item in self._get("/games"):
            if not isinstance(item, dict):
                continue
            stage = self._parse_stage(item)
            if stage is None:
                continue
            home_ref = self._team_ref(item, "home")
            away_ref = self._team_ref(item, "away")
            if home_ref is not None:
                refs.add(home_ref)
            if away_ref is not None:
                refs.add(away_ref)
        if not refs:
            raise ProviderError("No knockout team references were found in provider data.")
        return refs
