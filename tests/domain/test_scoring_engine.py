from app.domain.entities.scoring import ScoreLine, ScoringConfig
from app.domain.services.scoring_engine import ScoringEngine


def test_exact_score_awards_correct_winner_and_exact_bonus_only() -> None:
    result = ScoringEngine().calculate(
        prediction=ScoreLine(3, 1),
        actual=ScoreLine(3, 1),
    )

    assert result.points == 4
    assert result.correct_winner is True
    assert result.exact_score is True
    assert result.partial_home_goals is False
    assert result.partial_away_goals is False
    assert result.reasons == ("correct_winner", "exact_score")


def test_correct_winner_with_one_partial_goal_awards_three_points() -> None:
    result = ScoringEngine().calculate(
        prediction=ScoreLine(3, 1),
        actual=ScoreLine(3, 0),
    )

    assert result.points == 3
    assert result.correct_winner is True
    assert result.partial_home_goals is True
    assert result.partial_away_goals is False


def test_wrong_winner_with_partial_goal_only_awards_partial_point() -> None:
    result = ScoringEngine().calculate(
        prediction=ScoreLine(1, 2),
        actual=ScoreLine(1, 0),
    )

    assert result.points == 1
    assert result.correct_winner is False
    assert result.partial_home_goals is True


def test_scoring_is_configurable() -> None:
    engine = ScoringEngine(
        ScoringConfig(
            correct_winner_points=3,
            exact_score_points=5,
            partial_goal_points=2,
            version="custom",
        )
    )

    result = engine.calculate(ScoreLine(2, 0), ScoreLine(2, 1))

    assert result.points == 5
    assert result.scoring_version == "custom"


def test_correct_winner_can_use_declared_advancing_side_for_tied_actual() -> None:
    result = ScoringEngine().calculate(
        prediction=ScoreLine(2, 1),
        actual=ScoreLine(1, 1, declared_winner_side="home"),
    )

    assert result.points == 3
    assert result.correct_winner is True
    assert result.partial_away_goals is True


def test_tied_prediction_does_not_infer_advancing_side() -> None:
    result = ScoringEngine().calculate(
        prediction=ScoreLine(1, 1),
        actual=ScoreLine(1, 1, declared_winner_side="away"),
    )

    assert result.points == 2
    assert result.correct_winner is False
    assert result.exact_score is True


def test_tied_prediction_can_declare_correct_advancing_side() -> None:
    result = ScoringEngine().calculate(
        prediction=ScoreLine(1, 1, declared_winner_side="away"),
        actual=ScoreLine(1, 1, declared_winner_side="away"),
    )

    assert result.points == 4
    assert result.correct_winner is True
    assert result.exact_score is True


def test_tied_prediction_declared_wrong_side_gets_exact_score_only() -> None:
    result = ScoringEngine().calculate(
        prediction=ScoreLine(1, 1, declared_winner_side="home"),
        actual=ScoreLine(1, 1, declared_winner_side="away"),
    )

    assert result.points == 2
    assert result.correct_winner is False
    assert result.exact_score is True
