"""HumanAgent examples (BR-HUM-1..11, worked examples 4 and 5)."""

from __future__ import annotations

from dataclasses import replace

import pytest

from snake_vs_machine.agents.human import HumanAgent
from snake_vs_machine.core.setup import new_match
from snake_vs_machine.core.state import (
    Action,
    CoreConfig,
    Direction,
    EndReason,
    SnakeId,
    State,
)


def _facing(direction: Direction) -> State:
    state = new_match(CoreConfig(), seed=0)
    return replace(state, snake_a=replace(state.snake_a, direction=direction))


def test_empty_buffer_returns_straight_and_consumes_nothing() -> None:
    agent = HumanAgent()
    assert agent.act(_facing(Direction.E), SnakeId.A) is Action.straight
    assert agent.pending() == ()


def test_reverse_is_dropped_at_push() -> None:
    agent = HumanAgent()
    agent.act(_facing(Direction.E), SnakeId.A)
    agent.push_absolute(Direction.W)
    assert agent.pending() == ()


def test_redundant_command_is_dropped_at_push() -> None:
    agent = HumanAgent()
    agent.act(_facing(Direction.E), SnakeId.A)
    agent.push_absolute(Direction.E)
    assert agent.pending() == ()


def test_first_command_is_accepted_before_any_tick() -> None:
    """`_last_direction` is None, so there is nothing to validate against."""
    agent = HumanAgent()
    agent.push_absolute(Direction.W)
    assert agent.pending() == (Direction.W,)


def test_worked_example_4_chain_of_two_turns() -> None:
    agent = HumanAgent()
    agent.act(_facing(Direction.E), SnakeId.A)

    agent.push_absolute(Direction.N)
    agent.push_absolute(Direction.N)  # redundant against the buffered N
    agent.push_absolute(Direction.S)  # reverse of the buffered N
    agent.push_absolute(Direction.W)
    assert agent.pending() == (Direction.N, Direction.W)

    assert agent.act(_facing(Direction.E), SnakeId.A) is Action.turn_left
    assert agent.act(_facing(Direction.N), SnakeId.A) is Action.turn_left
    assert agent.pending() == ()


def test_worked_example_5_full_buffer_ignores_the_new_key() -> None:
    """Facing east, `up left down` pressed faster than the tick (D45 item 2)."""
    agent = HumanAgent()
    agent.act(_facing(Direction.E), SnakeId.A)

    agent.push_absolute(Direction.N)
    agent.push_absolute(Direction.W)
    agent.push_absolute(Direction.S)

    assert agent.pending() == (Direction.N, Direction.W)

    # Draining the buffer yields two left turns and never a reverse. Evicting
    # the oldest instead would leave [W, S], and popping W while still facing
    # east is exactly the reverse D13 forbids.
    assert agent.act(_facing(Direction.E), SnakeId.A) is Action.turn_left
    assert agent.act(_facing(Direction.N), SnakeId.A) is Action.turn_left


def test_right_turn_conversion() -> None:
    agent = HumanAgent()
    agent.act(_facing(Direction.E), SnakeId.A)
    agent.push_absolute(Direction.S)
    assert agent.act(_facing(Direction.E), SnakeId.A) is Action.turn_right


def test_command_equal_to_current_direction_resolves_to_straight() -> None:
    """Buffered against an older direction, then the snake already turned."""
    agent = HumanAgent()
    agent.act(_facing(Direction.E), SnakeId.A)
    agent.push_absolute(Direction.N)
    assert agent.act(_facing(Direction.N), SnakeId.A) is Action.straight


def test_popped_reverse_returns_straight() -> None:
    """Defensive BR-HUM-9.

    `push_absolute` cannot produce this state, so the buffer is seeded
    directly rather than adding a back door to the agent itself.
    """
    agent = HumanAgent()
    agent._buffer.append(Direction.W)
    assert agent.act(_facing(Direction.E), SnakeId.A) is Action.straight


def test_exactly_one_command_leaves_per_tick() -> None:
    agent = HumanAgent()
    agent.act(_facing(Direction.E), SnakeId.A)
    agent.push_absolute(Direction.N)
    agent.push_absolute(Direction.W)
    assert len(agent.pending()) == 2
    agent.act(_facing(Direction.E), SnakeId.A)
    assert len(agent.pending()) == 1
    agent.act(_facing(Direction.N), SnakeId.A)
    assert agent.pending() == ()


def test_rejects_terminal_state() -> None:
    agent = HumanAgent()
    state = replace(_facing(Direction.E), end_reason=EndReason.timeout)
    with pytest.raises(ValueError, match="terminal"):
        agent.act(state, SnakeId.A)


def test_rejects_dead_snake() -> None:
    state = _facing(Direction.E)
    state = replace(state, snake_a=replace(state.snake_a, alive=False))
    with pytest.raises(ValueError, match="dead snake A"):
        HumanAgent().act(state, SnakeId.A)


def test_act_records_the_observed_direction() -> None:
    """After a tick facing north, west is a legal command but south is not."""
    agent = HumanAgent()
    agent.act(_facing(Direction.N), SnakeId.A)
    agent.push_absolute(Direction.S)
    assert agent.pending() == ()
    agent.push_absolute(Direction.W)
    assert agent.pending() == (Direction.W,)
