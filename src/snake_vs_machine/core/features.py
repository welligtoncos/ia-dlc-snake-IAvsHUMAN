"""Egocentric feature vector (D38–D40). No numpy, pygame, or sklearn."""

from __future__ import annotations

from snake_vs_machine.core.queries import flood_fill_count, next_occupancy
from snake_vs_machine.core.state import (
    Action,
    Cell,
    Direction,
    Snake,
    SnakeId,
    State,
    add_cell,
    delta,
    in_bounds,
    next_head,
)

FEATURE_SCHEMA_VERSION = 1

_FEATURE_NAMES: tuple[str, ...] = (
    "danger_ahead",
    "danger_left",
    "danger_right",
    "dist_danger_ahead",
    "dist_danger_left",
    "dist_danger_right",
    "space_free_ahead",
    "space_free_left",
    "space_free_right",
    "food_ahead",
    "food_left",
    "food_right",
    "food_behind",
    "dist_food",
    "opponent_closer_to_food",
    "dist_opponent_head",
    "head_risk_ahead",
    "head_risk_left",
    "head_risk_right",
    "length_diff",
)

_ACTIONS: tuple[Action, Action, Action] = (
    Action.straight,
    Action.turn_left,
    Action.turn_right,
)

_FRAME: dict[Direction, tuple[Cell, Cell, Cell]] = {
    Direction.E: (Cell(1, 0), Cell(0, -1), Cell(0, 1)),
    Direction.W: (Cell(-1, 0), Cell(0, 1), Cell(0, -1)),
    Direction.N: (Cell(0, -1), Cell(-1, 0), Cell(1, 0)),
    Direction.S: (Cell(0, 1), Cell(1, 0), Cell(-1, 0)),
}


def feature_names() -> tuple[str, ...]:
    return _FEATURE_NAMES


def _dot(vec: Cell, basis: Cell) -> int:
    return vec.x * basis.x + vec.y * basis.y


def _manhattan(a: Cell, b: Cell) -> int:
    return abs(a.x - b.x) + abs(a.y - b.y)


def _blocked(state: State, cell: Cell, occ: frozenset[Cell]) -> bool:
    return not in_bounds(cell, state.width, state.height) or cell in state.obstacles or cell in occ


def _ray(state: State, landing: Cell, facing: Direction, occ: frozenset[Cell]) -> float:
    if _blocked(state, landing, occ):
        return 0.0
    count = 0
    cell = landing
    step = delta(facing)
    while not _blocked(state, cell, occ):
        count += 1
        cell = add_cell(cell, step)
    return min(1.0, count / max(state.width, state.height))


def _free_cell_count(state: State, me: Snake, opp: Snake) -> int:
    """Free cells by arithmetic: bodies and obstacles never overlap (P-ENG-NOOVERLAP)."""
    return (
        state.width * state.height - len(state.obstacles) - len(me.body) - len(opp.body)
    )


def _space(
    state: State,
    landing: Cell,
    occ: frozenset[Cell],
    free_cells: int,
) -> float:
    if free_cells <= 0:
        return 0.0
    n = flood_fill_count(state, landing, occupancy=occ, limit=200)
    return min(1.0, n / min(200, free_cells))


def _food_block(state: State, me: Snake, opp: Snake) -> tuple[int, int, int, int, float, int]:
    if state.food is None or state.food == me.head:
        return 0, 0, 0, 0, 1.0, 0
    food = state.food
    vec = Cell(food.x - me.head.x, food.y - me.head.y)
    forward, left, right = _FRAME[me.direction]
    ahead = 1 if _dot(vec, forward) > 0 else 0
    behind = 1 if _dot(vec, Cell(-forward.x, -forward.y)) > 0 else 0
    left_b = 1 if _dot(vec, left) > 0 else 0
    right_b = 1 if _dot(vec, right) > 0 else 0
    denom = state.width + state.height - 2
    dist_food = min(1.0, _manhattan(me.head, food) / denom)
    closer = 1 if _manhattan(opp.head, food) < _manhattan(me.head, food) else 0
    return ahead, left_b, right_b, behind, dist_food, closer


def extract_features(state: State, snake_id: SnakeId) -> tuple[int | float, ...]:
    if state.end_reason is not None or not state.snake(snake_id).alive:
        raise ValueError("extract_features requires a living snake in a non-terminal match")
    me = state.snake(snake_id)
    opp = state.opponent(snake_id)
    opp_next: set[Cell] = set()
    for action in _ACTIONS:
        nxt, _ = next_head(opp.head, opp.direction, action)
        if in_bounds(nxt, state.width, state.height):
            opp_next.add(nxt)
    free_cells = _free_cell_count(state, me, opp)
    danger: list[int] = []
    dist_danger: list[float] = []
    space_free: list[float] = []
    head_risk: list[int] = []
    for action in _ACTIONS:
        landing, facing = next_head(me.head, me.direction, action)
        occ = next_occupancy(state, snake_id, action)
        fatal = _blocked(state, landing, occ)
        danger.append(1 if fatal else 0)
        dist_danger.append(_ray(state, landing, facing, occ))
        space_free.append(0.0 if fatal else _space(state, landing, occ, free_cells))
        head_risk.append(
            1 if in_bounds(landing, state.width, state.height) and landing in opp_next else 0
        )
    fa, fl, fr, fb, dist_food, closer = _food_block(state, me, opp)
    dist_opp = min(1.0, _manhattan(me.head, opp.head) / (state.width + state.height - 2))
    return (
        danger[0],
        danger[1],
        danger[2],
        dist_danger[0],
        dist_danger[1],
        dist_danger[2],
        space_free[0],
        space_free[1],
        space_free[2],
        fa,
        fl,
        fr,
        fb,
        dist_food,
        closer,
        dist_opp,
        head_risk[0],
        head_risk[1],
        head_risk[2],
        me.length - opp.length,
    )
