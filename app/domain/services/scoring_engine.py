from app.domain.entities.scoring import ScoreLine, ScoringConfig, ScoringResult


class ScoringEngine:
    def __init__(self, config: ScoringConfig | None = None) -> None:
        self.config = config or ScoringConfig()

    def calculate(self, prediction: ScoreLine, actual: ScoreLine) -> ScoringResult:
        points = 0
        reasons: list[str] = []

        correct_winner = (
            prediction.winner_side is not None
            and prediction.winner_side == actual.winner_side
        )
        if correct_winner:
            points += self.config.correct_winner_points
            reasons.append("correct_winner")

        exact_score = (
            prediction.home_goals == actual.home_goals
            and prediction.away_goals == actual.away_goals
        )
        partial_home_goals = prediction.home_goals == actual.home_goals
        partial_away_goals = prediction.away_goals == actual.away_goals

        if exact_score:
            points += self.config.exact_score_points
            reasons.append("exact_score")
        else:
            if partial_home_goals:
                points += self.config.partial_goal_points
                reasons.append("partial_home_goals")
            if partial_away_goals:
                points += self.config.partial_goal_points
                reasons.append("partial_away_goals")

        return ScoringResult(
            points=points,
            correct_winner=correct_winner,
            exact_score=exact_score,
            partial_home_goals=partial_home_goals and not exact_score,
            partial_away_goals=partial_away_goals and not exact_score,
            scoring_version=self.config.version,
            reasons=tuple(reasons),
        )

