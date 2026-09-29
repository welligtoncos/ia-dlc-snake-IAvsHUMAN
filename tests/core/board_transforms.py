"""Whole-board rotate/mirror for tests (D38 / D41)."""

from __future__ import annotations

from dataclasses import replace

from snake_vs_machine.core.state import Cell, Direction, Snake, State

_ROT90_DIR = {
    Direction.N: Direction.E,
    Direction.E: Direction.S,
    Direction.S: Direction.W,
    Direction.W: Direction.N,
}
_ROT180_DIR = {
    Direction.N: Direction.S,
    Direction.S: Direction.N,
    Direction.E: Direction.W,
    Direction.W: Direction.E,
}
_ROT270_DIR = {
    Direction.N: Direction.W,
    Direction.W: Direction.S,
    Direction.S: Direction.E,
    Direction.E: Direction.N,
}
_MX_DIR = {
    Direction.E: Direction.W,
    Direction.W: Direction.E,
    Direction.N: Direction.N,
    Direction.S: Direction.S,
}
_MY_DIR = {
    Direction.N: Direction.S,
    Direction.S: Direction.N,
    Direction.E: Direction.E,
    Direction.W: Direction.W,
}


def map_cell(cell: Cell, kind: str, width: int, height: int) -> Cell:
    if kind == "rot90":
        return Cell(width - 1 - cell.y, cell.x)
    if kind == "rot180":
        return Cell(width - 1 - cell.x, height - 1 - cell.y)
    if kind == "rot270":
        return Cell(cell.y, height - 1 - cell.x)
    if kind == "mx":
        return Cell(width - 1 - cell.x, cell.y)
    if kind == "my":
        return Cell(cell.x, height - 1 - cell.y)
    raise ValueError(f"unknown transform {kind}")


def map_direction(direction: Direction, kind: str) -> Direction:
    table = {
        "rot90": _ROT90_DIR,
        "rot180": _ROT180_DIR,
        "rot270": _ROT270_DIR,
        "mx": _MX_DIR,
        "my": _MY_DIR,
    }[kind]
    return table[direction]


def _map_snake(snake: Snake, kind: str, width: int, height: int) -> Snake:
    return replace(
        snake,
        body=tuple(map_cell(c, kind, width, height) for c in snake.body),
        direction=map_direction(snake.direction, kind),
    )


def transform_state(state: State, kind: str) -> State:
    w, h = state.width, state.height
    food = None if state.food is None else map_cell(state.food, kind, w, h)
    return replace(
        state,
        snake_a=_map_snake(state.snake_a, kind, w, h),
        snake_b=_map_snake(state.snake_b, kind, w, h),
        food=food,
        obstacles=frozenset(map_cell(c, kind, w, h) for c in state.obstacles),
    )


def apply_n(state: State, kind: str, times: int) -> State:
    out = state
    for _ in range(times):
        out = transform_state(out, kind)
    return out
