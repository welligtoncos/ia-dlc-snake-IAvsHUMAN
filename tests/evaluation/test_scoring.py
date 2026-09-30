"""Scoring examples and P-MS-SCORE (BR-MS-7, D48 item 5, D60)."""

from __future__ import annotations

import pytest

from snake_vs_machine.core.state import EndReason, Outcome, Side, SnakeId
from snake_vs_machine.evaluation.scoring import (
    difference_ci,
    match_score,
    normal_ci,
    paired_difference_ci,
    summarise,
)
from snake_vs_machine.services.match import MatchResult


def _result(outcome: Outcome, seed: int = 0) -> MatchResult:
    return MatchResult(
        outcome=outcome,
        end_reason=EndReason.death,
        ticks=10,
        length_a=3,
        length_b=3,
        death_cause_a=None,
        death_cause_b=None,
        seed=seed,
        side_a=Side.NW,
        side_b=Side.SE,
    )


@pytest.mark.parametrize(
    ("outcome", "expected_a"),
    [(Outcome.win_a, 1.0), (Outcome.draw, 0.5), (Outcome.win_b, 0.0)],
)
def test_match_score_follows_the_outcome(outcome: Outcome, expected_a: float) -> None:
    result = _result(outcome)
    assert match_score(result, SnakeId.A) == expected_a


@pytest.mark.parametrize("outcome", list(Outcome))
def test_the_two_sides_always_sum_to_one(outcome: Outcome) -> None:
    result = _result(outcome)
    assert match_score(result, SnakeId.A) + match_score(result, SnakeId.B) == 1.0


def test_summarise_reports_the_draw_rate_separately() -> None:
    results = [
        _result(Outcome.win_a, 0),
        _result(Outcome.win_a, 1),
        _result(Outcome.draw, 2),
        _result(Outcome.win_b, 3),
    ]
    score = summarise(results)

    assert score.matches == 4
    assert score.points_a == 2.5
    assert score.points_b == 1.5
    assert score.score_rate_a == 0.625
    assert score.win_rate_a == 0.5
    assert score.win_rate_b == 0.25
    assert score.draw_rate == 0.25


def test_summarise_is_order_independent() -> None:
    results = [_result(Outcome.win_a, 0), _result(Outcome.draw, 1), _result(Outcome.win_b, 2)]
    assert summarise(results) == summarise(list(reversed(results)))


def test_summarise_rejects_an_empty_battery() -> None:
    with pytest.raises(ValueError, match="empty battery"):
        summarise([])


def test_normal_ci_is_none_for_n_less_than_two() -> None:
    assert normal_ci([1.0]) is None
    assert normal_ci([]) is None


def test_normal_ci_known_list() -> None:
    interval = normal_ci([1.0, 0.5, 0.0])
    assert interval is not None
    low, high = interval
    assert low < 0.5 < high


def test_paired_difference_ci_is_mean_of_diffs() -> None:
    interval = paired_difference_ci([1.0, 1.0, 0.5], [0.0, 0.5, 0.5])
    assert interval is not None
    low, high = interval
    assert low < (1.0 + 0.5 + 0.0) / 3 < high


def test_paired_difference_ci_rejects_unequal_length() -> None:
    with pytest.raises(ValueError, match="equal-length"):
        paired_difference_ci([1.0], [1.0, 0.0])


def test_difference_ci_none_when_short() -> None:
    assert difference_ci([1.0], [0.0, 1.0]) is None
