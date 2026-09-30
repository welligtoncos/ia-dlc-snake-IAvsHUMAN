"""The 1 / 0.5 / 0 mapping and its rates (D48 item 5, D14b).

Single home for the scoring rule. `MatchResult` deliberately carries no
score: `services` must not depend on `evaluation`, and `outcome` already
determines the points. U7 extends this module for tournaments.
"""

from __future__ import annotations

import math
import statistics
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from snake_vs_machine.core.state import Outcome, SnakeId
from snake_vs_machine.services.match import MatchResult

_Z95 = 1.96

_WIN = 1.0
_DRAW = 0.5
_LOSS = 0.0


def match_score(result: MatchResult, snake_id: SnakeId) -> float:
    """Points scored by one side in one match."""
    if result.outcome is Outcome.draw:
        return _DRAW
    winner = SnakeId.A if result.outcome is Outcome.win_a else SnakeId.B
    return _WIN if snake_id is winner else _LOSS


@dataclass(frozen=True, slots=True)
class BatteryScore:
    """Aggregate of a battery. The draw rate is reported on its own (BR-MS-7)."""

    matches: int
    points_a: float
    points_b: float
    score_rate_a: float
    win_rate_a: float
    win_rate_b: float
    draw_rate: float


def summarise(results: Iterable[MatchResult]) -> BatteryScore:
    """Aggregate a battery. Order-independent, so it suits `imap_unordered`."""
    collected = list(results)
    if not collected:
        raise ValueError("cannot summarise an empty battery")
    matches = len(collected)
    points_a = sum(match_score(r, SnakeId.A) for r in collected)
    wins_a = sum(1 for r in collected if r.outcome is Outcome.win_a)
    wins_b = sum(1 for r in collected if r.outcome is Outcome.win_b)
    draws = sum(1 for r in collected if r.outcome is Outcome.draw)
    return BatteryScore(
        matches=matches,
        points_a=points_a,
        points_b=matches - points_a,
        score_rate_a=points_a / matches,
        win_rate_a=wins_a / matches,
        win_rate_b=wins_b / matches,
        draw_rate=draws / matches,
    )


def normal_ci(scores: Sequence[float]) -> tuple[float, float] | None:
    """Mean ± 1.96 * sample_sd / sqrt(n). None when n < 2 (P-CI-WIDE)."""
    if len(scores) < 2:
        return None
    mean = statistics.fmean(scores)
    se = statistics.stdev(scores) / math.sqrt(len(scores))
    return (mean - _Z95 * se, mean + _Z95 * se)


def difference_ci(
    xs: Sequence[float], ys: Sequence[float]
) -> tuple[float, float] | None:
    """Unpaired difference of means. None if either n < 2."""
    if len(xs) < 2 or len(ys) < 2:
        return None
    gap = statistics.fmean(xs) - statistics.fmean(ys)
    se = math.sqrt(
        statistics.variance(xs) / len(xs) + statistics.variance(ys) / len(ys)
    )
    return (gap - _Z95 * se, gap + _Z95 * se)


def paired_difference_ci(
    xs: Sequence[float], ys: Sequence[float]
) -> tuple[float, float] | None:
    """Mean of per-match (x_i - y_i) ± 1.96 * s_d / sqrt(n) (D60)."""
    if len(xs) != len(ys):
        raise ValueError("paired_difference_ci requires equal-length series")
    diffs = [x - y for x, y in zip(xs, ys, strict=True)]
    return normal_ci(diffs)
