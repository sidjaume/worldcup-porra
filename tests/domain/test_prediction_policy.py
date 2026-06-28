from datetime import UTC, datetime, timedelta

from app.domain.enums import MatchStatus
from app.domain.services.prediction_policy import PredictionPolicy


def test_prediction_can_be_edited_before_scheduled_time() -> None:
    now = datetime(2026, 6, 28, 12, 0, tzinfo=UTC)

    assert PredictionPolicy().can_edit(
        scheduled_at=now + timedelta(minutes=1),
        status=MatchStatus.SCHEDULED,
        now=now,
    )


def test_prediction_cannot_be_edited_at_scheduled_time() -> None:
    now = datetime(2026, 6, 28, 12, 0, tzinfo=UTC)

    assert not PredictionPolicy().can_edit(
        scheduled_at=now,
        status=MatchStatus.SCHEDULED,
        now=now,
    )


def test_prediction_cannot_be_edited_when_match_started() -> None:
    now = datetime(2026, 6, 28, 12, 0, tzinfo=UTC)

    assert not PredictionPolicy().can_edit(
        scheduled_at=now + timedelta(minutes=10),
        status=MatchStatus.IN_PROGRESS,
        now=now,
    )

