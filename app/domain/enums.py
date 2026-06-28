from enum import StrEnum


class TournamentStage(StrEnum):
    ROUND_OF_32 = "round_of_32"
    ROUND_OF_16 = "round_of_16"
    QUARTER_FINAL = "quarter_final"
    SEMI_FINAL = "semi_final"
    FINAL = "final"


class MatchStatus(StrEnum):
    SCHEDULED = "scheduled"
    LOCKED = "locked"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PoolRole(StrEnum):
    OWNER = "owner"
    PARTICIPANT = "participant"


class ParticipantStatus(StrEnum):
    ACTIVE = "active"
    REMOVED = "removed"


class NextSlot(StrEnum):
    HOME = "home"
    AWAY = "away"


class PredictionStatus(StrEnum):
    EDITABLE = "editable"
    LOCKED = "locked"
    SCORED = "scored"

