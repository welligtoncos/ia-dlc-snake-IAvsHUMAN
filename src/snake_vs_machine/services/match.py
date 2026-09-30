"""Match loop: ask both agents, advance one tick, report facts (Q11=A).

Clock-free by design. Pacing belongs to the UI (D28), and latency belongs to
the `TimedAgent` wrapper in `evaluation` (D44 item 5). Scoring is not here
either: `outcome` determines it and `evaluation.scoring` owns the mapping
(D48 item 5).
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass

from snake_vs_machine.agents.base import ActResult, Agent, ExplainingAgent
from snake_vs_machine.core import engine
from snake_vs_machine.core.setup import new_match
from snake_vs_machine.core.state import (
    Action,
    CoreConfig,
    DeathCause,
    EndReason,
    Outcome,
    Side,
    SnakeId,
    State,
)

TickHook = Callable[[State, ActResult, ActResult, State], None]


@dataclass(frozen=True, slots=True)
class MatchResult:
    """Finished-match facts only. Holds no `State`, so batteries stay cheap."""

    outcome: Outcome
    end_reason: EndReason
    ticks: int
    length_a: int
    length_b: int
    death_cause_a: DeathCause | None
    death_cause_b: DeathCause | None
    seed: int
    side_a: Side
    side_b: Side


def _ask(agent: Agent, state: State, snake_id: SnakeId) -> ActResult:
    """One question per agent per tick, explanation included when offered."""
    if isinstance(agent, ExplainingAgent):
        result = agent.decide(state, snake_id)
        if not isinstance(result, ActResult):
            raise TypeError(
                f"{type(agent).__name__}.decide returned {result!r} for snake "
                f"{snake_id.name}; expected an ActResult"
            )
    else:
        result = ActResult(agent.act(state, snake_id), None)
    if not isinstance(result.action, Action):
        raise TypeError(
            f"{type(agent).__name__} returned {result.action!r} for snake "
            f"{snake_id.name}; expected an Action"
        )
    return result


def tick_with_results(
    state: State,
    agent_a: Agent,
    agent_b: Agent,
) -> tuple[State, ActResult, ActResult]:
    if state.end_reason is not None:
        raise ValueError("cannot tick a terminal state")
    # Both agents see the same pre-tick state: movement is simultaneous (D14).
    result_a = _ask(agent_a, state, SnakeId.A)
    result_b = _ask(agent_b, state, SnakeId.B)
    return engine.step(state, result_a.action, result_b.action), result_a, result_b


def tick(state: State, agent_a: Agent, agent_b: Agent) -> State:
    return tick_with_results(state, agent_a, agent_b)[0]


def _result(state: State) -> MatchResult:
    if state.end_reason is None:
        raise ValueError("cannot summarise a match that is still playing")
    return MatchResult(
        outcome=engine.outcome(state),
        end_reason=state.end_reason,
        ticks=state.tick,
        length_a=state.snake_a.length,
        length_b=state.snake_b.length,
        death_cause_a=state.snake_a.death_cause,
        death_cause_b=state.snake_b.death_cause,
        seed=state.seed,
        side_a=state.side_a,
        side_b=state.side_b,
    )


def play(
    agent_a: Agent,
    agent_b: Agent,
    config: CoreConfig,
    seed: int,
    sides: Mapping[SnakeId, Side] | None = None,
    on_tick: TickHook | None = None,
) -> MatchResult:
    """Play one match to termination.

    Side assignment comes from the caller (Q9=A): tournaments in U7 decide
    parity and pass `sides` through. Terminates within `config.max_ticks`
    because `engine.step` sets `timeout` there.
    """
    state = new_match(config, seed, sides)
    while not engine.is_terminal(state):
        before = state
        state, result_a, result_b = tick_with_results(state, agent_a, agent_b)
        if on_tick is not None:
            on_tick(before, result_a, result_b, state)
    return _result(state)
