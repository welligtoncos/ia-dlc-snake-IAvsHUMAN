"""Critical example tests written before engine implementation (D36 / TDD)."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace

import pytest

from snake_vs_machine.core.engine import outcome, step
from snake_vs_machine.core.setup import new_match
from snake_vs_machine.core.state import (
    Action,
    Cell,
    CoreConfig,
    DeathCause,
    Direction,
    EndReason,
    Outcome,
    State,
)


def _blank() -> State:
    return new_match(CoreConfig(), seed=0)


def _place(
    *,
    a_body: tuple[Cell, ...],
    a_dir: Direction,
    b_body: tuple[Cell, ...],
    b_dir: Direction,
    food: Cell,
) -> State:
    base = _blank()
    return replace(
        base,
        snake_a=replace(base.snake_a, body=a_body, direction=a_dir),
        snake_b=replace(base.snake_b, body=b_body, direction=b_dir),
        food=food,
        obstacles=frozenset(),
        tick=0,
        end_reason=None,
    )


def test_d32_ram_without_swap_opponent_body() -> None:
    """A (5,5) E, B (6,5) N, both straight → A opponent_body; B lives."""
    state = _place(
        a_body=(Cell(5, 5), Cell(4, 5), Cell(3, 5)),
        a_dir=Direction.E,
        b_body=(Cell(6, 5), Cell(6, 6), Cell(6, 7)),
        b_dir=Direction.N,
        food=Cell(10, 9),
    )
    nxt = step(state, Action.straight, Action.straight)
    assert not nxt.snake_a.alive
    assert nxt.snake_a.death_cause is DeathCause.opponent_body
    assert nxt.snake_b.alive
    assert nxt.snake_b.death_cause is None
    assert nxt.end_reason is EndReason.death
    assert outcome(nxt) is Outcome.win_b


def test_head_swap_equal_length_both_die() -> None:
    state = _place(
        a_body=(Cell(5, 5), Cell(4, 5), Cell(3, 5)),
        a_dir=Direction.E,
        b_body=(Cell(6, 5), Cell(7, 5), Cell(8, 5)),
        b_dir=Direction.W,
        food=Cell(10, 9),
    )
    nxt = step(state, Action.straight, Action.straight)
    assert not nxt.snake_a.alive
    assert not nxt.snake_b.alive
    assert nxt.snake_a.death_cause is DeathCause.head_to_head
    assert nxt.snake_b.death_cause is DeathCause.head_to_head
    assert outcome(nxt) is Outcome.draw


def test_d33_opponent_tail_vacates_when_not_eating() -> None:
    """B adjacent to food, turns away; A steps onto B's tail and survives."""
    food = Cell(5, 5)
    state = _place(
        a_body=(Cell(2, 6), Cell(1, 6), Cell(0, 6)),
        a_dir=Direction.E,
        b_body=(Cell(5, 6), Cell(4, 6), Cell(3, 6)),
        b_dir=Direction.E,
        food=food,
    )
    # B head (5,6) is 4-adj to food (5,5). turn_right from E → S → (5,7), not food.
    # A straight from (2,6) → (3,6) = B tail.
    nxt = step(state, Action.straight, Action.turn_right)
    assert nxt.snake_a.alive
    assert nxt.snake_a.head == Cell(3, 6)
    assert nxt.snake_b.alive
    assert nxt.snake_b.head == Cell(5, 7)


def test_d33_opponent_tail_solid_when_eating() -> None:
    food = Cell(6, 6)
    state = _place(
        a_body=(Cell(2, 6), Cell(1, 6), Cell(0, 6)),
        a_dir=Direction.E,
        b_body=(Cell(5, 6), Cell(4, 6), Cell(3, 6)),
        b_dir=Direction.E,
        food=food,
    )
    # B straight E → (6,6) food; tail (3,6) stays. A straight → (3,6).
    nxt = step(state, Action.straight, Action.straight)
    assert not nxt.snake_a.alive
    assert nxt.snake_a.death_cause is DeathCause.opponent_body
    assert nxt.snake_b.alive
    assert nxt.food != food


def test_h2h_on_food_equal_size_food_stays() -> None:
    food = Cell(10, 9)
    state = _place(
        a_body=(Cell(9, 9), Cell(8, 9), Cell(7, 9)),
        a_dir=Direction.E,
        b_body=(Cell(11, 9), Cell(12, 9), Cell(13, 9)),
        b_dir=Direction.W,
        food=food,
    )
    nxt = step(state, Action.straight, Action.straight)
    assert not nxt.snake_a.alive
    assert not nxt.snake_b.alive
    assert nxt.snake_a.death_cause is DeathCause.head_to_head
    assert nxt.snake_b.death_cause is DeathCause.head_to_head
    assert nxt.food == food
    assert outcome(nxt) is Outcome.draw


def test_simultaneous_death_draw_records_each_cause() -> None:
    """A walks into the west wall; B walks into the east wall."""
    state = _place(
        a_body=(Cell(0, 5), Cell(1, 5), Cell(2, 5)),
        a_dir=Direction.W,
        b_body=(Cell(19, 5), Cell(18, 5), Cell(17, 5)),
        b_dir=Direction.E,
        food=Cell(10, 9),
    )
    nxt = step(state, Action.straight, Action.straight)
    assert not nxt.snake_a.alive
    assert not nxt.snake_b.alive
    assert nxt.snake_a.death_cause is DeathCause.wall
    assert nxt.snake_b.death_cause is DeathCause.wall
    assert nxt.end_reason is EndReason.death
    assert outcome(nxt) is Outcome.draw


def test_d35_state_is_hashable_and_frozen() -> None:
    state = _blank()
    assert hash(state) == hash(state)
    with pytest.raises(FrozenInstanceError):
        state.tick = 1  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        state.snake_a.alive = False  # type: ignore[misc]
