"""Batteries of matches, sequential or across processes (D48 item 1).

`run_match` lives here, at module level in an installed package, because the
Windows `spawn` start method re-imports the worker's module in the child. A
worker defined inside a `scripts/` `__main__` block would not survive that.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from multiprocessing import Pool, cpu_count

from snake_vs_machine.agents.registry import AgentSpec, build_agent
from snake_vs_machine.core.state import CoreConfig, Side, SnakeId
from snake_vs_machine.services.match import MatchResult, play


@dataclass(frozen=True, slots=True)
class MatchTask:
    """One match, described entirely by picklable values."""

    spec_a: AgentSpec
    spec_b: AgentSpec
    config: CoreConfig
    seed: int
    sides: Mapping[SnakeId, Side] | None = None


def run_match(task: MatchTask) -> MatchResult:
    """The worker. Builds both agents locally, then plays one match."""
    return play(
        build_agent(task.spec_a),
        build_agent(task.spec_b),
        task.config,
        task.seed,
        task.sides,
    )


def run_sequential(tasks: Iterable[MatchTask]) -> list[MatchResult]:
    return [run_match(task) for task in tasks]


def _chunksize(count: int, processes: int) -> int:
    """A few chunks per process: enough to balance, few enough to amortise."""
    return max(1, count // (processes * 4))


def run_imap[T, R](
    worker: Callable[[T], R],
    tasks: Sequence[T],
    processes: int | None = None,
    chunksize: int | None = None,
) -> list[R]:
    """Generic `imap_unordered` pool used by match batteries, collect and DAgger.

    `processes=1` stays in-process so unit tests do not pay for Windows `spawn`.
    Results come back in completion order when a pool is used.

    D60: on this Windows host `Pool` has hung for U5 joblib workers; scripts
    default to `--processes 1`. See decisions.md D60.
    """
    if not tasks:
        return []
    workers = processes if processes is not None else max(1, cpu_count() - 1)
    if workers == 1:
        return [worker(task) for task in tasks]
    size = chunksize if chunksize is not None else _chunksize(len(tasks), workers)
    with Pool(processes=workers) as pool:
        return list(pool.imap_unordered(worker, tasks, chunksize=size))


def run_parallel(
    tasks: Sequence[MatchTask],
    processes: int | None = None,
    chunksize: int | None = None,
) -> list[MatchResult]:
    """Play the battery across processes, leaving one core for the desktop.

    Results come back in completion order, which is what `imap_unordered`
    buys. Anything that compares batteries must sort by seed first.
    """
    return run_imap(run_match, tasks, processes=processes, chunksize=chunksize)


def by_seed(results: Iterable[MatchResult]) -> list[MatchResult]:
    """Canonical order for comparing two batteries (D48 item 1)."""
    return sorted(results, key=lambda r: r.seed)
