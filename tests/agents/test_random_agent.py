"""RandomAgent examples (BR-RND-1..4)."""

from __future__ import annotations

from dataclasses import replace

import pytest

from snake_vs_machine.agents.base import ACTIONS
from snake_vs_machine.agents.random_agent import RandomAgent
from snake_vs_machine.core.queries import is_fatal
from snake_vs_machine.core.setup import new_match
from snake_vs_machine.core.state import (
    Action,
    Cell,
    CoreConfig,
    Direction,
    EndReason,
    Snake,
    SnakeId,
    State,
)


def _kickoff(seed: int = 0) -> State:
    return new_match(CoreConfig(), seed=seed)


def _boxed_state() -> State:
    """Snake A facing east with a wall ahead and obstacles left and right.

    Head at (19, 0): east is out of the board, north is out of the board, and
    (19, 1) is an obstacle. Every action is fatal.
    """
    state = _kickoff()
    snake_a = Snake(
        id=SnakeId.A,
        body=(Cell(19, 0), Cell(18, 0), Cell(17, 0)),
        direction=Direction.E,
    )
    return replace(state, snake_a=snake_a, obstacles=frozenset({Cell(19, 1)}))


def test_chooses_a_non_fatal_action_when_one_exists() -> None:
    state = _kickoff()
    chosen = RandomAgent().act(state, SnakeId.A)
    assert not is_fatal(state, SnakeId.A, chosen)


def test_falls_back_to_all_three_when_every_action_is_fatal() -> None:
    state = _boxed_state()
    assert all(is_fatal(state, SnakeId.A, a) for a in ACTIONS)
    assert RandomAgent().act(state, SnakeId.A) in ACTIONS


def test_pure_across_fresh_instances() -> None:
    state = _kickoff(seed=12)
    assert RandomAgent().act(state, SnakeId.A) == RandomAgent().act(state, SnakeId.A)


def test_the_two_snakes_draw_independently() -> None:
    """Different streams per side: over many seeds the pair is not always equal."""
    state_actions = [
        (RandomAgent().act(s, SnakeId.A), RandomAgent().act(s, SnakeId.B))
        for s in (_kickoff(seed=i) for i in range(20))
    ]
    assert any(a != b for a, b in state_actions)


def test_every_non_fatal_action_appears_over_many_ticks() -> None:
    """No silent bias to `straight` (BR-RND-4)."""
    seen: set[Action] = set()
    for seed in range(60):
        state = _kickoff(seed=seed)
        seen.add(RandomAgent().act(state, SnakeId.A))
    assert seen == set(ACTIONS)


def test_rejects_terminal_state() -> None:
    state = replace(_kickoff(), end_reason=EndReason.timeout)
    with pytest.raises(ValueError, match="terminal"):
        RandomAgent().act(state, SnakeId.A)


def test_rejects_dead_snake() -> None:
    state = _kickoff()
    state = replace(state, snake_a=replace(state.snake_a, alive=False))
    with pytest.raises(ValueError, match="dead snake A"):
        RandomAgent().act(state, SnakeId.A)
