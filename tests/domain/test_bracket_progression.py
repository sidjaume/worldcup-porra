from uuid import uuid4

import pytest

from app.domain.enums import NextSlot
from app.domain.errors import InvalidMatchResultError
from app.domain.services.bracket_progression import BracketProgression, MatchProgression


def test_winner_advances_to_home_slot() -> None:
    winner_id = uuid4()
    next_match_id = uuid4()

    assignment = BracketProgression().advance(
        MatchProgression(
            winner_team_id=winner_id,
            next_match_id=next_match_id,
            next_match_slot=NextSlot.HOME,
        )
    )

    assert assignment is not None
    assert assignment.next_match_id == next_match_id
    assert assignment.home_team_id == winner_id
    assert assignment.away_team_id is None


def test_final_match_has_no_progression_assignment() -> None:
    assignment = BracketProgression().advance(
        MatchProgression(
            winner_team_id=uuid4(),
            next_match_id=None,
            next_match_slot=None,
        )
    )

    assert assignment is None


def test_progression_requires_winner() -> None:
    with pytest.raises(InvalidMatchResultError):
        BracketProgression().advance(
            MatchProgression(
                winner_team_id=None,
                next_match_id=uuid4(),
                next_match_slot=NextSlot.AWAY,
            )
        )

