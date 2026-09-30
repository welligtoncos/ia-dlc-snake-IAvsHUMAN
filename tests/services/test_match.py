"""MatchService examples (BR-MS-1..9, U3-REL-1..5)."""

from __future__ import annotations

from dataclasses import dataclass, replace

import pytest

from snake_vs_machine.agents.base import ActResult
from snake_vs_machine.agents.expert import ExpertAgent
from snake_vs_machine.agents.random_agent import RandomAgent
from snake_vs_machine.core import engine
from snake_vs_machine.core.setup import new_match
from snake_vs_machine.core.state import (
    Action,
    CoreConfig,
    EndReason,
    Outcome,
    Side,
    SnakeId,
    State,
)
from snake_vs_machine.services import match


class FixedAgent:
    """Plays one action forever."""

    def __init__(self, action: Action) -> None:
        self._action = action

    def act(self, state: State, snake_id: SnakeId) -> Action:
        return self._action


@dataclass(frozen=True, slots=True)
class FakePayload:
    """Stands in for U5's explanation; `services` must not look inside."""

    note: str


class TalkingAgent:
    """Implements `decide`, so `MatchService` must route through it."""

    def __init__(self, action: Action) -> None:
        self._action = action
        self.decide_calls = 0

    def act(self, state: State, snake_id: SnakeId) -> Action:
        raise AssertionError("act must not be called when decide exists")

    def decide(self, state: State, snake_id: SnakeId) -> ActResult:
        self.decide_calls += 1
        return ActResult(self._action, FakePayload(f"tick {state.tick}"))


class SilentDecide:
    """`decide` exists but returns a bare Action, not an ActResult."""

    def act(self, state: State, snake_id: SnakeId) -> Action:
        return Action.straight

    def decide(self, state: State, snake_id: SnakeId) -> ActResult:
        return Action.straight  # type: ignore[return-value]


class BrokenAgent:
    """Returns something that is not an Action."""

    def act(self, state: State, snake_id: SnakeId) -> Action:
        return "turn_left"  # type: ignore[return-value]


class ExplodingAgent:
    def act(self, state: State, snake_id: SnakeId) -> Action:
        raise RuntimeError("boom")


def _kickoff(seed: int = 0) -> State:
    return new_match(CoreConfig(), seed=seed)


def test_tick_matches_engine_step_for_plain_agents() -> None:
    state = _kickoff()
    agent_a = FixedAgent(Action.straight)
    agent_b = FixedAgent(Action.turn_left)
    expected = engine.step(state, Action.straight, Action.turn_left)
    assert match.tick(state, agent_a, agent_b) == expected


def test_tick_rejects_a_terminal_state() -> None:
    state = replace(_kickoff(), end_reason=EndReason.timeout)
    with pytest.raises(ValueError, match="terminal"):
        match.tick(state, RandomAgent(), RandomAgent())


def test_decide_is_used_once_per_tick_and_the_payload_reaches_the_hook() -> None:
    talker = TalkingAgent(Action.straight)
    seen: list[ActResult] = []

    def hook(before: State, result_a: ActResult, result_b: ActResult, after: State) -> None:
        seen.append(result_a)

    result = match.play(
        talker,
        FixedAgent(Action.straight),
        CoreConfig(max_ticks=5),
        seed=3,
        on_tick=hook,
    )

    assert talker.decide_calls == result.ticks
    assert len(seen) == result.ticks
    assert all(isinstance(r.explanation, FakePayload) for r in seen)
    assert seen[0].explanation == FakePayload("tick 0")


def test_plain_agents_produce_a_none_explanation() -> None:
    seen: list[ActResult] = []

    def hook(before: State, result_a: ActResult, result_b: ActResult, after: State) -> None:
        seen.append(result_b)

    match.play(
        FixedAgent(Action.straight),
        FixedAgent(Action.straight),
        CoreConfig(max_ticks=4),
        seed=3,
        on_tick=hook,
    )
    assert all(r.explanation is None for r in seen)


def test_non_action_return_raises_naming_the_agent_and_the_side() -> None:
    with pytest.raises(TypeError, match=r"BrokenAgent .* snake B"):
        match.tick(_kickoff(), RandomAgent(), BrokenAgent())


def test_decide_returning_a_bare_action_raises_naming_the_agent_and_the_side() -> None:
    with pytest.raises(TypeError, match=r"SilentDecide\.decide .* snake A"):
        match.tick(_kickoff(), SilentDecide(), RandomAgent())


def test_agent_exception_propagates_unchanged() -> None:
    with pytest.raises(RuntimeError, match="boom"):
        match.tick(_kickoff(), ExplodingAgent(), RandomAgent())


def test_play_terminates_and_reports_facts() -> None:
    result = match.play(RandomAgent(), RandomAgent(), CoreConfig(max_ticks=50), seed=7)
    assert result.end_reason is not None
    assert result.ticks <= 50
    assert result.seed == 7
    assert result.side_a is Side.NW
    assert result.side_b is Side.SE
    assert result.outcome in (Outcome.win_a, Outcome.win_b, Outcome.draw)


def test_play_honours_the_side_assignment() -> None:
    result = match.play(
        RandomAgent(),
        RandomAgent(),
        CoreConfig(max_ticks=10),
        seed=7,
        sides={SnakeId.A: Side.SE, SnakeId.B: Side.NW},
    )
    assert result.side_a is Side.SE
    assert result.side_b is Side.NW


def test_replay_is_identical() -> None:
    args = (RandomAgent(), RandomAgent(), CoreConfig(max_ticks=200), 11)
    assert match.play(*args) == match.play(*args)


def test_hook_fires_once_per_tick() -> None:
    calls: list[tuple[int, int]] = []

    def hook(before: State, result_a: ActResult, result_b: ActResult, after: State) -> None:
        calls.append((before.tick, after.tick))

    result = match.play(
        ExpertAgent(),
        RandomAgent(),
        CoreConfig(max_ticks=40),
        seed=5,
        on_tick=hook,
    )
    assert len(calls) == result.ticks
    assert calls == [(i, i + 1) for i in range(result.ticks)]


def test_tick_with_results_returns_explanations_and_tick_stays_state_only() -> None:
    from pathlib import Path

    from snake_vs_machine.agents.tree import TreeAgent, TreeExplanation

    path = Path(__file__).resolve().parents[2] / "models" / "fixtures" / "tiny_depth3.joblib"
    tree = TreeAgent.from_joblib(path, safety_mask=False)
    state = _kickoff(0)
    nxt, result_a, result_b = match.tick_with_results(state, tree, FixedAgent(Action.straight))
    assert isinstance(nxt, State)
    assert isinstance(result_a.explanation, TreeExplanation)
    assert match.tick(state, tree, FixedAgent(Action.straight)) == nxt
    assert result_b.explanation is None


def test_result_rejects_an_unfinished_state() -> None:
    with pytest.raises(ValueError, match="still playing"):
        match._result(_kickoff())
