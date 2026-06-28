from dataclasses import dataclass, field


@dataclass(frozen=True)
class ScoringConfig:
    correct_winner_points: int = 2
    exact_score_points: int = 2
    partial_goal_points: int = 1
    version: str = "mvp-2026-v1"


@dataclass(frozen=True)
class ScoreLine:
    home_goals: int
    away_goals: int

    def __post_init__(self) -> None:
        if self.home_goals < 0 or self.away_goals < 0:
            raise ValueError("Goals must be non-negative.")

    @property
    def winner_side(self) -> str | None:
        if self.home_goals > self.away_goals:
            return "home"
        if self.away_goals > self.home_goals:
            return "away"
        return None


@dataclass(frozen=True)
class ScoringResult:
    points: int
    correct_winner: bool
    exact_score: bool
    partial_home_goals: bool
    partial_away_goals: bool
    scoring_version: str
    reasons: tuple[str, ...] = field(default_factory=tuple)

