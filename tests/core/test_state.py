"""State immutability and kickoff helpers."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from snake_vs_machine.core.setup import new_match
from snake_vs_machine.core.state import Cell, CoreConfig, Side, SnakeId, copy


def test_copy_equals_and_hash() -> None:
    state = new_match(CoreConfig(), seed=7)
    cloned = copy(state)
    assert cloned == state
    assert hash(cloned) == hash(state)


def test_frozen_instance_error_on_assign() -> None:
    state = new_match(CoreConfig(), seed=1)
    with pytest.raises(FrozenInstanceError):
        state.tick = 99  # type: ignore[misc]


def test_snake_accessor() -> None:
    state = new_match(CoreConfig(), seed=0)
    assert state.snake(SnakeId.A) is state.snake_a
    assert state.snake(SnakeId.B) is state.snake_b
    assert state.side_a is Side.NW
    assert state.side_b is Side.SE


def test_kickoff_food_is_10_9() -> None:
    state = new_match(CoreConfig(), seed=0)
    assert state.food == Cell(10, 9)
    assert state.snake_a.head == Cell(2, 2)
    assert state.snake_b.head == Cell(17, 17)
