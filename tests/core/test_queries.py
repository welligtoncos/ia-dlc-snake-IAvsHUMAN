"""Occupancy, is_fatal (D29/D32), flood fill."""

from __future__ import annotations

import pytest

from snake_vs_machine.core.engine import step
from snake_vs_machine.core.queries import (
    flood_fill_count,
    is_fatal,
    next_occupancy,
    reachable_cells,
)
from snake_vs_machine.core.setup import new_match
from snake_vs_machine.core.state import Action, Cell, CoreConfig, Direction, SnakeId
from tests.core.board_transforms import map_cell, transform_state
from tests.core.test_engine_critical import _place


def test_d29_conservative_tail_solid_when_opponent_adj_food() -> None:
    food = Cell(5, 5)
    state = _place(
        a_body=(Cell(2, 6), Cell(1, 6), Cell(0, 6)),
        a_dir=Direction.E,
        b_body=(Cell(5, 6), Cell(4, 6), Cell(3, 6)),
        b_dir=Direction.E,
        food=food,
    )
    tail = Cell(3, 6)
    conservative = next_occupancy(state, SnakeId.A, Action.straight)
    real = next_occupancy(state, SnakeId.A, Action.straight, Action.turn_right)
    assert tail in conservative
    assert tail not in real
    assert is_fatal(state, SnakeId.A, Action.straight)
    nxt = step(state, Action.straight, Action.turn_right)
    assert nxt.snake_a.alive


def test_d32_ram_is_fatal_for_a_not_for_b() -> None:
    state = _place(
        a_body=(Cell(5, 5), Cell(4, 5), Cell(3, 5)),
        a_dir=Direction.E,
        b_body=(Cell(6, 5), Cell(6, 6), Cell(6, 7)),
        b_dir=Direction.N,
        food=Cell(10, 9),
    )
    assert is_fatal(state, SnakeId.A, Action.straight)
    assert not is_fatal(state, SnakeId.B, Action.straight)


def test_same_cell_h2h_on_third_cell_is_not_fatal() -> None:
    state = _place(
        a_body=(Cell(9, 9), Cell(8, 9), Cell(7, 9)),
        a_dir=Direction.E,
        b_body=(Cell(11, 9), Cell(12, 9), Cell(13, 9)),
        b_dir=Direction.W,
        food=Cell(0, 0),
    )
    assert not is_fatal(state, SnakeId.A, Action.straight)
    assert not is_fatal(state, SnakeId.B, Action.straight)


def test_occupancy_includes_both_heads() -> None:
    state = new_match(CoreConfig(), seed=0)
    occ = next_occupancy(state, SnakeId.A, Action.straight)
    assert state.snake_a.head in occ
    assert state.snake_b.head in occ


def test_flood_fill_blocked_start_is_empty() -> None:
    state = new_match(CoreConfig(), seed=0)
    assert flood_fill_count(state, state.snake_a.head) == 0
    assert reachable_cells(state, state.snake_a.head) == frozenset()


def test_flood_fill_food_is_walkable() -> None:
    state = new_match(CoreConfig(), seed=0)
    assert state.food is not None
    cells = reachable_cells(state, state.food, limit=20)
    assert state.food in cells
    assert len(cells) == 20


def test_flood_fill_respects_custom_occupancy() -> None:
    state = new_match(CoreConfig(), seed=0)
    start = Cell(10, 10)
    cells = reachable_cells(state, start, occupancy=frozenset(), limit=5)
    assert len(cells) == 5
    assert flood_fill_count(state, start, occupancy=frozenset(), limit=5) == 5


def test_flood_fill_obstacle_start() -> None:
    state = new_match(CoreConfig(obstacle_count=8), seed=3)
    if not state.obstacles:
        return
    cell = next(iter(state.obstacles))
    assert flood_fill_count(state, cell) == 0


def test_flood_fill_out_of_bounds_start_is_empty() -> None:
    state = new_match(CoreConfig(), seed=0)
    assert reachable_cells(state, Cell(-1, 0)) == frozenset()
    assert flood_fill_count(state, Cell(state.width, 0)) == 0


@pytest.mark.parametrize("limit", [0, -1])
def test_flood_fill_rejects_limit_below_one(limit: int) -> None:
    state = new_match(CoreConfig(), seed=0)
    assert state.food is not None
    with pytest.raises(ValueError):
        reachable_cells(state, state.food, limit=limit)
    with pytest.raises(ValueError):
        flood_fill_count(state, state.food, limit=limit)


@pytest.mark.parametrize("kind", ["rot90", "rot180", "rot270", "mx", "my"])
@pytest.mark.parametrize("limit", [50, 200])
def test_flood_fill_count_isometry_after_board_transform(kind: str, limit: int) -> None:
    """Count is min(reachable, limit) and unchanged by rotate/mirror (D39)."""
    state = new_match(CoreConfig(obstacle_count=4), seed=3)
    assert state.food is not None
    start = state.food
    before = flood_fill_count(state, start, limit=limit)
    full = flood_fill_count(state, start, limit=state.width * state.height)
    assert before == min(full, limit)
    transformed = transform_state(state, kind)
    after = flood_fill_count(
        transformed,
        map_cell(start, kind, state.width, state.height),
        limit=limit,
    )
    assert after == before
