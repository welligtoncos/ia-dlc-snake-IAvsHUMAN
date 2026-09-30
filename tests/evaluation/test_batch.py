"""Sequential vs parallel batteries produce the same results (P-MS-PARITY, D48 item 3)."""

from __future__ import annotations

from snake_vs_machine.agents.registry import AgentSpec
from snake_vs_machine.core.state import CoreConfig
from snake_vs_machine.evaluation.batch import (
    MatchTask,
    _chunksize,
    by_seed,
    run_imap,
    run_match,
    run_parallel,
    run_sequential,
)

_SEEDS = tuple(range(20))
_CONFIG = CoreConfig(max_ticks=60)


def _tasks() -> list[MatchTask]:
    spec = AgentSpec("random")
    return [MatchTask(spec, spec, _CONFIG, seed) for seed in _SEEDS]


def test_run_match_plays_one_seed() -> None:
    result = run_match(_tasks()[0])
    assert result.seed == 0
    assert result.end_reason is not None
    assert result.ticks <= _CONFIG.max_ticks


def test_p_ms_parity_sequential_matches_parallel() -> None:
    tasks = _tasks()
    sequential = by_seed(run_sequential(tasks))
    parallel = by_seed(run_parallel(tasks, processes=2, chunksize=2))
    assert sequential == parallel
    assert [r.seed for r in sequential] == list(_SEEDS)


def test_by_seed_orders_regardless_of_input() -> None:
    tasks = list(reversed(_tasks()))
    results = run_sequential(tasks)
    assert [r.seed for r in by_seed(results)] == list(_SEEDS)


def test_empty_parallel_battery_is_empty() -> None:
    assert run_parallel([]) == []


def test_chunksize_is_at_least_one() -> None:
    assert _chunksize(20, 2) == 2
    assert _chunksize(1, 8) == 1


def test_run_imap_identity_and_empty() -> None:
    assert run_imap(lambda x: x + 1, [1, 2, 3], processes=1) == [2, 3, 4]
    assert run_imap(lambda x: x, [], processes=1) == []
