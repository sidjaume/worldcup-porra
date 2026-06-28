from datetime import UTC, datetime

from app.domain.enums import MatchStatus


class PredictionPolicy:
    def can_edit(
        self,
        *,
        scheduled_at: datetime,
        status: MatchStatus,
        now: datetime | None = None,
    ) -> bool:
        now = now or datetime.now(UTC)
        if scheduled_at.tzinfo is None:
            scheduled_at = scheduled_at.replace(tzinfo=UTC)
        return status == MatchStatus.SCHEDULED and now < scheduled_at

