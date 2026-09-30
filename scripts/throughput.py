"""Throughput of random vs random and expert variants (D46 item 9, RNF03).

Prints the numbers that go into `aidlc-docs/construction/u3-agents/benchmark.md`.
Workers live in `evaluation.batch`, not here — Windows `spawn` re-imports
the worker module in the child.
"""

from __future__ import annotations

import time
from multiprocessing import cpu_count

from snake_vs_machine.agents.registry import AgentSpec
from snake_vs_machine.core.state import CoreConfig
from snake_vs_machine.evaluation.batch import MatchTask, run_parallel, run_sequential
from snake_vs_machine.services.match import MatchResult


def _tasks(name_a: str, name_b: str, count: int, config: CoreConfig) -> list[MatchTask]:
    spec_a = AgentSpec(name_a)
    spec_b = AgentSpec(name_b)
    return [MatchTask(spec_a, spec_b, config, seed) for seed in range(count)]


def _report(label: str, results: list[MatchResult], elapsed: float) -> None:
    ticks = sum(r.ticks for r in results)
    matches_per_min = len(results) / elapsed * 60.0
    ticks_per_s = ticks / elapsed
    print(
        f"{label}: n={len(results)} elapsed={elapsed:.3f}s "
        f"matches/min={matches_per_min:.1f} ticks/s={ticks_per_s:.1f} "
        f"mean_ticks={ticks / len(results):.1f}"
    )


def main() -> None:
    config = CoreConfig()
    workers = max(1, cpu_count() - 1)
    print(f"processes={workers} cpu_count={cpu_count()}")

    sequential = _tasks("random", "random", 40, config)
    start = time.perf_counter()
    seq_results = run_sequential(sequential)
    _report("random vs random sequential", seq_results, time.perf_counter() - start)

    parallel = _tasks("random", "random", 200, config)
    start = time.perf_counter()
    par_results = run_parallel(parallel, processes=workers)
    _report("random vs random parallel", par_results, time.perf_counter() - start)

    start = time.perf_counter()
    _report(
        "expert vs expert sequential",
        run_sequential(_tasks("expert", "expert", 20, config)),
        time.perf_counter() - start,
    )
    start = time.perf_counter()
    _report(
        "expert vs random sequential",
        run_sequential(_tasks("expert", "random", 20, config)),
        time.perf_counter() - start,
    )


if __name__ == "__main__":
    main()
