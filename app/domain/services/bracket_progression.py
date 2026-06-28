from dataclasses import dataclass
from uuid import UUID

from app.domain.enums import NextSlot
from app.domain.errors import BracketProgressionError, InvalidMatchResultError


@dataclass(frozen=True)
class MatchProgression:
    winner_team_id: UUID | None
    next_match_id: UUID | None
    next_match_slot: NextSlot | None


@dataclass(frozen=True)
class NextMatchAssignment:
    next_match_id: UUID
    home_team_id: UUID | None = None
    away_team_id: UUID | None = None


class BracketProgression:
    def advance(self, progression: MatchProgression) -> NextMatchAssignment | None:
        if progression.winner_team_id is None:
            raise InvalidMatchResultError("Completed knockout match requires a winner.")
        if progression.next_match_id is None:
            return None
        if progression.next_match_slot is None:
            raise BracketProgressionError("Next match slot is required.")

        if progression.next_match_slot == NextSlot.HOME:
            return NextMatchAssignment(
                next_match_id=progression.next_match_id,
                home_team_id=progression.winner_team_id,
            )
        return NextMatchAssignment(
            next_match_id=progression.next_match_id,
            away_team_id=progression.winner_team_id,
        )

