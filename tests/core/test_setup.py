"""Setup: symmetry, zones, determinism."""

from __future__ import annotations

import pytest

from snake_vs_machine.core.setup import SetupError, new_match
from snake_vs_machine.core.state import Cell, CoreConfig, Side, SnakeId


def _rot180(cell: Cell, width: int, height: int) -> Cell:
    return Cell(width - 1 - cell.x, height - 1 - cell.y)


def test_same_seed_same_match() -> None:
    cfg = CoreConfig(obstacle_count=8)
    assert new_match(cfg, seed=42) == new_match(cfg, seed=42)


def test_obstacles_are_180_symmetric() -> None:
    state = new_match(CoreConfig(obstacle_count=8), seed=3)
    for cell in state.obstacles:
        assert _rot180(cell, state.width, state.height) in state.obstacles


def test_obstacles_avoid_chebyshev_spawn_zones() -> None:
    state = new_match(CoreConfig(obstacle_count=8), seed=11)
    forbidden = {
        Cell(2 + dx, 2 + dy) for dx in range(-2, 3) for dy in range(-2, 3)
    }
    forbidden |= {Cell(3 + dx, 2 + dy) for dx in range(-2, 3) for dy in range(-2, 3)}
    forbidden |= {Cell(17 + dx, 17 + dy) for dx in range(-2, 3) for dy in range(-2, 3)}
    forbidden |= {Cell(16 + dx, 17 + dy) for dx in range(-2, 3) for dy in range(-2, 3)}
    assert state.obstacles.isdisjoint(forbidden)
    assert Cell(10, 9) not in state.obstacles


def test_sides_argument_is_not_stored_as_mapping() -> None:
    state = new_match(
        CoreConfig(),
        seed=0,
        sides={SnakeId.A: Side.SE, SnakeId.B: Side.NW},
    )
    assert state.side_a is Side.SE
    assert state.snake_a.head == Cell(17, 17)
    assert "snakes" not in state.__slots__


def test_odd_obstacle_count_rounds_up_to_even() -> None:
    state = new_match(CoreConfig(obstacle_count=3), seed=5)
    assert len(state.obstacles) == 4


def test_setup_error_when_too_many_obstacles() -> None:
    with pytest.raises(SetupError):
        new_match(CoreConfig(obstacle_count=400), seed=0)
