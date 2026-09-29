"""Tick rules: simultaneous movement, collisions, food (D32–D35)."""

from __future__ import annotations

from dataclasses import replace

import numpy as np

from snake_vs_machine.core.queries import body_cells, next_occupancy
from snake_vs_machine.core.state import (
    Action,
    Cell,
    DeathCause,
    Direction,
    EndReason,
    Outcome,
    Snake,
    SnakeId,
    State,
    copy,
    in_bounds,
    next_head,
)


def is_terminal(state: State) -> bool:
    return state.end_reason is not None


def outcome(state: State) -> Outcome:
    if not state.snake_a.alive and not state.snake_b.alive:
        return Outcome.draw
    if not state.snake_a.alive:
        return Outcome.win_b
    if not state.snake_b.alive:
        return Outcome.win_a
    if state.end_reason is EndReason.timeout:
        if state.snake_a.length > state.snake_b.length:
            return Outcome.win_a
        if state.snake_b.length > state.snake_a.length:
            return Outcome.win_b
        return Outcome.draw
    raise ValueError("outcome is undefined while the match is still playing")


def _classify(
    state: State,
    snake: Snake,
    nxt: Cell,
    occ: frozenset[Cell],
    opponent_head: Cell,
    swap: bool,
) -> DeathCause | None:
    if not in_bounds(nxt, state.width, state.height):
        return DeathCause.wall
    if nxt in state.obstacles:
        return DeathCause.obstacle
    if nxt == opponent_head and swap:
        return None
    if nxt in occ:
        if nxt in snake.body:
            return DeathCause.self_body
        return DeathCause.opponent_body
    return None


def _apply_body(
    snake: Snake,
    nxt: Cell,
    facing: Direction,
    intends_eat: bool,
    alive: bool,
    cause: DeathCause | None,
) -> Snake:
    if not alive:
        return replace(snake, alive=False, death_cause=cause)
    new_body = (nxt,) + snake.body if intends_eat else (nxt,) + snake.body[:-1]
    return replace(snake, body=new_body, direction=facing, alive=True, death_cause=None)


def _respawn_food(state: State, snake_a: Snake, snake_b: Snake, tick_after: int) -> Cell | None:
    blocked = set(snake_a.body) | set(snake_b.body) | set(state.obstacles)
    free = [
        Cell(x, y)
        for y in range(state.height)
        for x in range(state.width)
        if Cell(x, y) not in blocked
    ]
    if not free:
        return None
    rng = np.random.default_rng(np.random.SeedSequence([int(state.seed), int(tick_after)]))
    index = int(rng.choice(len(free)))
    return free[index]


def step(state: State, action_a: Action, action_b: Action) -> State:
    if is_terminal(state):
        return copy(state)

    snake_a = state.snake_a
    snake_b = state.snake_b
    next_a, dir_a = next_head(snake_a.head, snake_a.direction, action_a)
    next_b, dir_b = next_head(snake_b.head, snake_b.direction, action_b)
    intends_a = state.food is not None and next_a == state.food
    intends_b = state.food is not None and next_b == state.food
    swap = next_a == snake_b.head and next_b == snake_a.head

    bodies = body_cells(state)
    occ_a = next_occupancy(state, SnakeId.A, action_a, action_b, bodies=bodies)
    occ_b = next_occupancy(state, SnakeId.B, action_b, action_a, bodies=bodies)

    cause_a = _classify(state, snake_a, next_a, occ_a, snake_b.head, swap)
    cause_b = _classify(state, snake_b, next_b, occ_b, snake_a.head, swap)

    meet = next_a == next_b
    if meet or swap:
        cand_a = cause_a is None
        cand_b = cause_b is None
        if cand_a and cand_b:
            if snake_a.length < snake_b.length:
                cause_a = DeathCause.head_to_head
            elif snake_b.length < snake_a.length:
                cause_b = DeathCause.head_to_head
            else:
                cause_a = DeathCause.head_to_head
                cause_b = DeathCause.head_to_head

    alive_a = cause_a is None
    alive_b = cause_b is None
    new_a = _apply_body(snake_a, next_a, dir_a, intends_a, alive_a, cause_a)
    new_b = _apply_body(snake_b, next_b, dir_b, intends_b, alive_b, cause_b)

    tick_after = state.tick + 1
    food = state.food
    if (alive_a and intends_a) or (alive_b and intends_b):
        food = _respawn_food(state, new_a, new_b, tick_after)

    if not alive_a or not alive_b:
        end_reason = EndReason.death
    elif tick_after >= state.max_ticks:
        end_reason = EndReason.timeout
    else:
        end_reason = None

    return replace(
        state,
        snake_a=new_a,
        snake_b=new_b,
        food=food,
        tick=tick_after,
        end_reason=end_reason,
    )
