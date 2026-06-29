from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

from app.domain.enums import ParticipantStatus
from app.services.prediction_service import PredictionService


class FakePoolsRepository:
    def __init__(self, *, pool_id, participant_user_id) -> None:
        self.pool_id = pool_id
        self.participant_user_id = participant_user_id

    def get(self, pool_id):
        if pool_id == self.pool_id:
            return SimpleNamespace(id=pool_id, is_active=True)
        return None

    def get_participant(self, *, pool_id, user_id):
        if pool_id == self.pool_id and user_id == self.participant_user_id:
            return SimpleNamespace(status=ParticipantStatus.ACTIVE)
        return None


class FakePredictionsRepository:
    def __init__(self, rows) -> None:
        self.rows = rows

    def list_scored_rows(self, pool_id):
        return list(self.rows)


def test_rankings_use_earliest_joined_at_as_final_tie_breaker() -> None:
    pool_id = uuid4()
    requesting_user_id = uuid4()
    earlier_user_id = uuid4()
    later_user_id = uuid4()

    later_user = SimpleNamespace(id=later_user_id, display_name="Alice")
    earlier_user = SimpleNamespace(id=earlier_user_id, display_name="Zoe")

    rows = [
        (
            later_user,
            8,
            2,
            3,
            4,
            5,
            datetime(2026, 6, 29, 13, tzinfo=UTC),
        ),
        (
            earlier_user,
            8,
            2,
            3,
            4,
            5,
            datetime(2026, 6, 29, 12, tzinfo=UTC),
        ),
    ]

    service = PredictionService(
        SimpleNamespace(),
        SimpleNamespace(scoring_version="test"),
    )
    service.pools = FakePoolsRepository(
        pool_id=pool_id,
        participant_user_id=requesting_user_id,
    )
    service.predictions = FakePredictionsRepository(rows)

    rankings = service.rankings(pool_id=pool_id, user_id=requesting_user_id)

    assert [row[0].id for row in rankings] == [earlier_user_id, later_user_id]
