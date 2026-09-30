"""Match kickoff: spawns, food, obstacles (D25, D26, D29, D31)."""

from __future__ import annotations

from collections.abc import Mapping

from snake_vs_machine.core.rng import obstacle_generator
from snake_vs_machine.core.state import (
    Cell,
    CoreConfig,
    Direction,
    Side,
    Snake,
    SnakeId,
    State,
    in_bounds,
    neighbors4,
)

_NW_BODY = (Cell(2, 2), Cell(1, 2), Cell(0, 2))
_SE_BODY = (Cell(17, 17), Cell(18, 17), Cell(19, 17))
_NW_DIR = Direction.E
_SE_DIR = Direction.W
_NW_AHEAD = Cell(3, 2)
_SE_AHEAD = Cell(16, 17)
_FOOD_SCAN_START = Cell(10, 9)


class SetupError(Exception):
    """Raised when obstacle generation fails after 100 attempts."""


def _template(side: Side, snake_id: SnakeId) -> Snake:
    if side is Side.NW:
        return Snake(id=snake_id, body=_NW_BODY, direction=_NW_DIR)
    return Snake(id=snake_id, body=_SE_BODY, direction=_SE_DIR)


def _scan_food(width: int, height: int, blocked: frozenset[Cell]) -> Cell:
    cells = [Cell(x, y) for y in range(height) for x in range(width)]
    try:
        start = cells.index(_FOOD_SCAN_START)
    except ValueError:
        start = 0
    for i in range(len(cells)):
        cell = cells[(start + i) % len(cells)]
        if cell not in blocked:
            return cell
    raise SetupError("no free cell for initial food")


def _rot180(cell: Cell, width: int, height: int) -> Cell:
    return Cell(width - 1 - cell.x, height - 1 - cell.y)


def _chebyshev_disk(center: Cell) -> frozenset[Cell]:
    return frozenset(
        Cell(center.x + dx, center.y + dy) for dx in range(-2, 3) for dy in range(-2, 3)
    )


def _forbidden(
    snake_a: Snake,
    snake_b: Snake,
    food: Cell,
    side_a: Side,
    side_b: Side,
) -> frozenset[Cell]:
    ahead = {
        Side.NW: _NW_AHEAD,
        Side.SE: _SE_AHEAD,
    }
    cells = set(_chebyshev_disk(snake_a.head))
    cells |= _chebyshev_disk(snake_b.head)
    cells |= _chebyshev_disk(ahead[side_a])
    cells |= _chebyshev_disk(ahead[side_b])
    cells.update(snake_a.body)
    cells.update(snake_b.body)
    cells.add(food)
    return frozenset(cells)


def _free_connected(
    width: int,
    height: int,
    obstacles: frozenset[Cell],
    initial_bodies: frozenset[Cell],
) -> bool:
    free: list[Cell] = []
    for y in range(height):
        for x in range(width):
            cell = Cell(x, y)
            if cell not in obstacles and cell not in initial_bodies:
                free.append(cell)
    if not free:
        return True
    start = free[0]
    seen = {start}
    stack = [start]
    while stack:
        cell = stack.pop()
        for nxt in neighbors4(cell):
            if (
                in_bounds(nxt, width, height)
                and nxt not in obstacles
                and nxt not in initial_bodies
                and nxt not in seen
            ):
                seen.add(nxt)
                stack.append(nxt)
    return len(seen) == len(free)


def _generate_obstacles(
    config: CoreConfig,
    seed: int,
    snake_a: Snake,
    snake_b: Snake,
    food: Cell,
    side_a: Side,
    side_b: Side,
) -> frozenset[Cell]:
    if config.obstacle_count == 0:
        return frozenset()
    n = config.obstacle_count if config.obstacle_count % 2 == 0 else config.obstacle_count + 1
    bodies = frozenset(snake_a.body + snake_b.body)
    forbid = _forbidden(snake_a, snake_b, food, side_a, side_b)
    width, height = config.width, config.height
    for k in range(100):
        rng = obstacle_generator(seed, k)
        pairs: list[tuple[Cell, Cell]] = []
        for y in range(height):
            for x in range(width):
                cell = Cell(x, y)
                complement = _rot180(cell, width, height)
                if (cell.x, cell.y) >= (complement.x, complement.y):
                    continue
                if cell in forbid or complement in forbid:
                    continue
                if not in_bounds(complement, width, height):
                    continue
                pairs.append((cell, complement))
        rng.shuffle(pairs)
        if len(pairs) < n // 2:
            continue
        chosen = pairs[: n // 2]
        obstacles = frozenset(cell for pair in chosen for cell in pair)
        if _free_connected(width, height, obstacles, bodies):
            return obstacles
    raise SetupError("obstacle generation failed after 100 attempts")


def new_match(
    config: CoreConfig,
    seed: int,
    sides: Mapping[SnakeId, Side] | None = None,
) -> State:
    """Build a deterministic kickoff State. `sides` is not stored as a mapping."""
    side_a = Side.NW
    side_b = Side.SE
    if sides is not None:
        side_a = sides[SnakeId.A]
        side_b = sides[SnakeId.B]
    snake_a = _template(side_a, SnakeId.A)
    snake_b = _template(side_b, SnakeId.B)
    food = _scan_food(config.width, config.height, frozenset(snake_a.body + snake_b.body))
    obstacles = _generate_obstacles(config, seed, snake_a, snake_b, food, side_a, side_b)
    return State(
        width=config.width,
        height=config.height,
        max_ticks=config.max_ticks,
        tick=0,
        seed=seed,
        snake_a=snake_a,
        snake_b=snake_b,
        food=food,
        obstacles=obstacles,
        end_reason=None,
        side_a=side_a,
        side_b=side_b,
    )
