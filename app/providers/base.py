"""Provider adapter base types and protocol.

All external data sources must implement the ProviderAdapter protocol and
normalise their payload into ProviderTeam / ProviderMatch value objects before
returning data to the application layer.

Constraints (from ARCH-003):
- Providers may update: external ref IDs, home/away teams, scheduled kickoff,
  match status, end-of-play goals, winner/advancing team, last-updated metadata.
- Providers must NOT: decide scoring rules, calculate rankings, bypass auth/audit.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, runtime_checkable

from app.domain.enums import MatchStatus, TournamentStage


@dataclass(frozen=True)
class ProviderTeam:
    """Normalised team record from a provider."""

    provider_ref: str
    name: str
    short_name: str | None = None
    fifa_code: str | None = None
    flag_url: str | None = None


@dataclass(frozen=True)
class ProviderMatch:
    """Normalised match record from a provider.

    Scores represent end-of-play goals (regulation + extra time).
    Penalty shoot-out goals must never be included.
    For penalty-decided matches, winner_provider_ref holds the advancing team;
    home_score and away_score may be equal (tied).
    """

    provider_ref: str
    stage: TournamentStage
    bracket_position: int
    scheduled_at: datetime
    status: MatchStatus
    home_team_provider_ref: str | None = None
    away_team_provider_ref: str | None = None
    home_score: int | None = None
    away_score: int | None = None
    # Advancing team — set even when scores are tied (penalty winner)
    winner_provider_ref: str | None = None


@runtime_checkable
class ProviderAdapter(Protocol):
    """Protocol that all provider adapters must satisfy."""

    def fetch_teams(self, tournament_year: int) -> list[ProviderTeam]:
        """Return all teams for the given tournament year.

        Must filter to the teams relevant to the knockout subset if the
        provider covers the full tournament.
        """
        ...

    def fetch_matches(self, tournament_year: int) -> list[ProviderMatch]:
        """Return knockout-phase matches for the given tournament year.

        Must filter to the stages supported by this application:
        round_of_32, round_of_16, quarter_final, semi_final, final.
        Must exclude group-stage matches, qualification matches, and
        third-place play-off matches.
        """
        ...
