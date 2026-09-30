"""Property-based tests for MatchService (P-MS-TERM, P-MS-REPLAY, P-MS-HOOK)."""

from __future__ import annotations

from hypothesis import given
from hypothesis import strategies as st

from snake_vs_machine.agents.base import ActResult
from snake_vs_machine.agents.expert import ExpertAgent
from snake_vs_machine.agents.random_agent import RandomAgent
from snake_vs_machine.core import engine
from snake_vs_machine.core.setup import new_match
from snake_vs_machine.core.state import CoreConfig, Side, SnakeId, State
from snake_vs_machine.services import match


@st.composite
def short_config_and_seed(draw: st.DrawFn) -> tuple[CoreConfig, int]:
    seed = draw(st.integers(min_value=0, max_value=50_000))
    obstacle_count = draw(st.integers(min_value=0, max_value=8))
    max_ticks = draw(st.integers(min_value=8, max_value=60))
    return CoreConfig(max_ticks=max_ticks, obstacle_count=obstacle_count), seed


@given(short_config_and_seed())
def test_p_ms_term(data: tuple[CoreConfig, int]) -> None:
    config, seed = data
    result = match.play(RandomAgent(), ExpertAgent(), config, seed)
    assert result.end_reason is not None
    assert result.ticks <= config.max_ticks


@given(short_config_and_seed())
def test_p_ms_replay(data: tuple[CoreConfig, int]) -> None:
    config, seed = data
    first = match.play(RandomAgent(), RandomAgent(), config, seed)
    second = match.play(RandomAgent(), RandomAgent(), config, seed)
    assert first == second


@given(short_config_and_seed(), st.sampled_from((None, {SnakeId.A: Side.SE, SnakeId.B: Side.NW})))
def test_p_ms_hook(data: tuple[CoreConfig, int], sides: dict[SnakeId, Side] | None) -> None:
    config, seed = data
    actions: list[tuple[object, object]] = []

    def hook(before: State, result_a: ActResult, result_b: ActResult, after: State) -> None:
        actions.append((result_a.action, result_b.action))

    result = match.play(
        RandomAgent(),
        ExpertAgent(),
        config,
        seed,
        sides=sides,
        on_tick=hook,
    )
    assert len(actions) == result.ticks

    replayed = new_match(config, seed, sides)
    for action_a, action_b in actions:
        replayed = engine.step(replayed, action_a, action_b)
    assert engine.is_terminal(replayed)
    assert replayed.tick == result.ticks
    assert engine.outcome(replayed) is result.outcome
