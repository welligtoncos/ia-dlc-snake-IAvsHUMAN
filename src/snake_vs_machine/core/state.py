"""Immutable match values (D34, D35)."""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum, auto
from typing import NamedTuple


class SnakeId(Enum):
    A = auto()
    B = auto()


class Side(Enum):
    NW = auto()
    SE = auto()


class Direction(Enum):
    N = auto()
    E = auto()
    S = auto()
    W = auto()


class Action(Enum):
    straight = auto()
    turn_left = auto()
    turn_right = auto()


class DeathCause(Enum):
    wall = auto()
    obstacle = auto()
    self_body = auto()
    opponent_body = auto()
    head_to_head = auto()


class EndReason(Enum):
    death = auto()
    timeout = auto()


class Outcome(Enum):
    win_a = auto()
    win_b = auto()
    draw = auto()


class Cell(NamedTuple):
    x: int
    y: int


_DELTA: dict[Direction, Cell] = {
    Direction.E: Cell(1, 0),
    Direction.W: Cell(-1, 0),
    Direction.N: Cell(0, -1),
    Direction.S: Cell(0, 1),
}

_LEFT: dict[Direction, Direction] = {
    Direction.N: Direction.W,
    Direction.E: Direction.N,
    Direction.S: Direction.E,
    Direction.W: Direction.S,
}

_RIGHT: dict[Direction, Direction] = {
    Direction.N: Direction.E,
    Direction.E: Direction.S,
    Direction.S: Direction.W,
    Direction.W: Direction.N,
}


def delta(direction: Direction) -> Cell:
    return _DELTA[direction]


def apply_action(direction: Direction, action: Action) -> Direction:
    if action is Action.straight:
        return direction
    if action is Action.turn_left:
        return _LEFT[direction]
    return _RIGHT[direction]


def add_cell(cell: Cell, d: Cell) -> Cell:
    return Cell(cell.x + d.x, cell.y + d.y)


def next_head(head: Cell, direction: Direction, action: Action) -> tuple[Cell, Direction]:
    facing = apply_action(direction, action)
    return add_cell(head, delta(facing)), facing


def neighbors4(cell: Cell) -> tuple[Cell, Cell, Cell, Cell]:
    return (
        Cell(cell.x + 1, cell.y),
        Cell(cell.x - 1, cell.y),
        Cell(cell.x, cell.y + 1),
        Cell(cell.x, cell.y - 1),
    )


def in_bounds(cell: Cell, width: int, height: int) -> bool:
    return 0 <= cell.x < width and 0 <= cell.y < height


@dataclass(frozen=True, slots=True)
class Snake:
    id: SnakeId
    body: tuple[Cell, ...]
    direction: Direction
    alive: bool = True
    death_cause: DeathCause | None = None

    @property
    def head(self) -> Cell:
        return self.body[0]

    @property
    def tail(self) -> Cell:
        return self.body[-1]

    @property
    def length(self) -> int:
        return len(self.body)


@dataclass(frozen=True, slots=True)
class CoreConfig:
    width: int = 20
    height: int = 20
    max_ticks: int = 1800
    obstacle_count: int = 0


@dataclass(frozen=True, slots=True)
class State:
    width: int
    height: int
    max_ticks: int
    tick: int
    seed: int
    snake_a: Snake
    snake_b: Snake
    food: Cell | None
    obstacles: frozenset[Cell]
    end_reason: EndReason | None
    side_a: Side
    side_b: Side

    def snake(self, snake_id: SnakeId) -> Snake:
        if snake_id is SnakeId.A:
            return self.snake_a
        return self.snake_b

    def opponent(self, snake_id: SnakeId) -> Snake:
        if snake_id is SnakeId.A:
            return self.snake_b
        return self.snake_a


def copy(state: State) -> State:
    """Identity copy: values are frozen (P-COPY)."""
    return replace(state)
