"""ExpertAgent decision latency (D46 item 2, D48 item 4).

Rows printed for `aidlc-docs/construction/u3-agents/benchmark.md`:
- worst case: kickoff, obstacle_count=0
- typical: mean per decision across expert vs expert matches
"""

from __future__ import annotations

import time

from snake_vs_machine.agents.expert import ExpertAgent
from snake_vs_machine.core.setup import new_match
from snake_vs_machine.core.state import CoreConfig, SnakeId, State
from snake_vs_machine.services.match import play


class _TimedExpert:
    """Script-only wrapper. Agents themselves stay clock-free."""

    def __init__(self) -> None:
        self.inner = ExpertAgent()
        self.samples: list[float] = []

    def act(self, state: State, snake_id: SnakeId) -> object:
        started = time.perf_counter()
        action = self.inner.act(state, snake_id)
        self.samples.append(time.perf_counter() - started)
        return action


def _mean_ms(samples: list[float]) -> float:
    return (sum(samples) / len(samples)) * 1000.0


def _max_ms(samples: list[float]) -> float:
    return max(samples) * 1000.0


def main() -> None:
    budget_ms = 1.0
    kickoff = new_match(CoreConfig(obstacle_count=0), seed=0)
    agent = ExpertAgent()
    repeats = 400
    samples: list[float] = []
    for _ in range(repeats):
        started = time.perf_counter()
        agent.act(kickoff, SnakeId.A)
        samples.append(time.perf_counter() - started)
    worst_mean = _mean_ms(samples)
    worst_max = _max_ms(samples)
    status = "OK" if worst_max <= budget_ms else "ALERTA"
    print(
        f"kickoff obstacle_count=0: mean={worst_mean:.3f} ms "
        f"max={worst_max:.3f} ms n={repeats} budget=1.0 ms {status}"
    )

    timed_a = _TimedExpert()
    timed_b = _TimedExpert()
    for seed in range(3):
        play(timed_a, timed_b, CoreConfig(), seed=seed)
    typical = timed_a.samples + timed_b.samples
    typical_mean = _mean_ms(typical)
    typical_status = "OK" if typical_mean <= budget_ms else "ALERTA"
    print(
        f"expert vs expert mean per decision: mean={typical_mean:.3f} ms "
        f"max={_max_ms(typical):.3f} ms n={len(typical)} budget=1.0 ms {typical_status}"
    )


if __name__ == "__main__":
    main()
