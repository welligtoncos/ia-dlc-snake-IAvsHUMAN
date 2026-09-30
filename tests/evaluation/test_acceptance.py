"""Expert vs random acceptance (BR-U3-ACC1/2, D46 item 8, D48 item 3)."""

from __future__ import annotations

from pathlib import Path

import pytest

from snake_vs_machine.agents.registry import AgentSpec
from snake_vs_machine.core.state import CoreConfig, SnakeId
from snake_vs_machine.evaluation.batch import MatchTask, run_sequential
from snake_vs_machine.evaluation.scoring import match_score, summarise

_REPO = Path(__file__).resolve().parents[2]
_TINY = _REPO / "models" / "fixtures" / "tiny_depth3.joblib"
_BC6 = _REPO / "models" / "bc_depth6.joblib"
_BC8 = _REPO / "models" / "bc_depth8.joblib"

_EXPERT = AgentSpec("expert")
_RANDOM = AgentSpec("random")


def _battery(n: int, config: CoreConfig) -> list[MatchTask]:
    return [MatchTask(_EXPERT, _RANDOM, config, seed) for seed in range(n)]


def test_reduced_expert_vs_random_battery() -> None:
    """Fast smoke of the acceptance path; the 95% bar lives on the slow test."""
    results = run_sequential(_battery(8, CoreConfig(max_ticks=80)))
    score = summarise(results)
    assert score.matches == 8
    assert score.draw_rate + score.win_rate_a + score.win_rate_b == pytest.approx(1.0)
    assert all(
        match_score(result, SnakeId.A) + match_score(result, SnakeId.B) == 1.0 for result in results
    )


@pytest.mark.slow
def test_expert_scores_at_least_95_percent_vs_random_over_500_matches() -> None:
    """Single-process (D48 item 3). Excluded from the default run."""
    results = run_sequential(_battery(500, CoreConfig()))
    score = summarise(results)
    assert score.matches == 500
    assert score.score_rate_a >= 0.95


def test_reduced_bc_vs_random_battery() -> None:
    spec = AgentSpec("tree", {"path": str(_TINY), "safety_mask": False})
    tasks = [MatchTask(spec, _RANDOM, CoreConfig(max_ticks=80), seed) for seed in range(8)]
    results = run_sequential(tasks)
    score = summarise(results)
    assert score.matches == 8
    assert score.draw_rate + score.win_rate_a + score.win_rate_b == pytest.approx(1.0)


@pytest.mark.slow
def test_bc6_and_bc8_acceptance_vs_random_over_500() -> None:
    """Closing bar (D52). Skips until the real models exist."""
    if not _BC6.is_file() or not _BC8.is_file():
        pytest.skip("real BC models are produced by scripts/train_bc.py")
    config = CoreConfig()
    for path in (_BC6, _BC8):
        spec = AgentSpec("tree", {"path": str(path), "safety_mask": False})
        tasks = [MatchTask(spec, _RANDOM, config, seed) for seed in range(500)]
        score = summarise(run_sequential(tasks))
        assert score.matches == 500
        assert score.score_rate_a >= 0.90
