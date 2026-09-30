"""Wall-clock wrapper around any agent (D59 item 7). Not inside MatchService."""

from __future__ import annotations

import time
from typing import Any

from snake_vs_machine.agents.base import ActResult, Agent
from snake_vs_machine.agents.registry import build_agent
from snake_vs_machine.core.state import Action, SnakeId, State
from snake_vs_machine.evaluation.batch import MatchTask
from snake_vs_machine.services.match import MatchResult, play


class TimedAgent:
    """Times `decide` when present, otherwise `act`. `act` delegates to `decide`."""

    def __init__(self, inner: Agent) -> None:
        self._inner = inner
        self._times: list[float] = []

    def decide(self, state: State, snake_id: SnakeId) -> ActResult:
        started = time.perf_counter()
        decide = getattr(self._inner, "decide", None)
        result: ActResult
        if callable(decide):
            raw: Any = decide(state, snake_id)
            if not isinstance(raw, ActResult):
                raise TypeError(
                    f"{type(self._inner).__name__}.decide returned {raw!r}"
                )
            result = raw
        else:
            result = ActResult(self._inner.act(state, snake_id))
        self._times.append(time.perf_counter() - started)
        return result

    def act(self, state: State, snake_id: SnakeId) -> Action:
        return self.decide(state, snake_id).action

    @property
    def mean_ms(self) -> float:
        if not self._times:
            return float("nan")
        return 1000.0 * sum(self._times) / len(self._times)

    @property
    def samples(self) -> int:
        return len(self._times)


def run_timed_match(task: MatchTask) -> tuple[MatchResult, float, float]:
    """Module-level worker: play one match with TimedAgent on both sides."""
    agent_a = TimedAgent(build_agent(task.spec_a))
    agent_b = TimedAgent(build_agent(task.spec_b))
    result = play(agent_a, agent_b, task.config, task.seed, task.sides)
    return result, agent_a.mean_ms, agent_b.mean_ms
