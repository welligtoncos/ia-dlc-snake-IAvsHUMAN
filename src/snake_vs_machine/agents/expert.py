"""Heuristic expert: safety, then space, then food (D44 item 1).

No A*. Food distance comes from a single BFS run backwards from the food,
which is exact rather than approximate — see the argument in
`aidlc-docs/construction/u3-agents/functional-design/business-logic-model.md`.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from snake_vs_machine.agents.base import ACTIONS, ensure_playable, snake_index
from snake_vs_machine.core.queries import body_cells, flood_fill_count, next_occupancy
from snake_vs_machine.core.rng import agent_generator
from snake_vs_machine.core.state import (
    Action,
    Cell,
    SnakeId,
    State,
    in_bounds,
    next_head,
)

_FLOOD_LIMIT = 200
_UNVISITED = -1
_BLOCKED = -2


@dataclass(frozen=True, slots=True)
class ActionEvaluation:
    """Everything the decision order needs about one relative action."""

    action: Action
    landing: Cell
    occupancy: frozenset[Cell]
    fatal: bool
    head_risk: bool
    flood: int
    food_distance: int | None


@dataclass(frozen=True, slots=True)
class ExpertDecision:
    """The chosen action plus why, so tests can assert the reasoning."""

    action: Action
    stage: str
    drawn: bool
    evaluations: tuple[ActionEvaluation, ...]


def _food_distances(state: State, blocked: frozenset[Cell]) -> list[int] | None:
    """BFS from the food over row-major indices; no cap, it is a distance.

    Returns a grid where `>= 0` is the step count, `_UNVISITED` means
    unreachable and `_BLOCKED` means solid. `None` when there is no food.
    """
    food = state.food
    if food is None:
        return None
    width = state.width
    size = width * state.height
    dist = [_UNVISITED] * size
    for cell in blocked:
        if in_bounds(cell, width, state.height):
            dist[cell.y * width + cell.x] = _BLOCKED
    start = food.y * width + food.x
    dist[start] = 0
    order = [start]
    head = 0
    while head < len(order):
        idx = order[head]
        head += 1
        step = dist[idx] + 1
        x = idx % width
        if x > 0 and dist[idx - 1] == _UNVISITED:
            dist[idx - 1] = step
            order.append(idx - 1)
        if x + 1 < width and dist[idx + 1] == _UNVISITED:
            dist[idx + 1] = step
            order.append(idx + 1)
        if idx >= width and dist[idx - width] == _UNVISITED:
            dist[idx - width] = step
            order.append(idx - width)
        if idx + width < size and dist[idx + width] == _UNVISITED:
            dist[idx + width] = step
            order.append(idx + width)
    return dist


def _lookup(state: State, dist: list[int] | None, landing: Cell) -> int | None:
    if dist is None or not in_bounds(landing, state.width, state.height):
        return None
    value = dist[landing.y * state.width + landing.x]
    return value if value >= 0 else None


def _opponent_next_heads(state: State, snake_id: SnakeId) -> frozenset[Cell]:
    opp = state.opponent(snake_id)
    return frozenset(
        cell
        for cell in (next_head(opp.head, opp.direction, a)[0] for a in ACTIONS)
        if in_bounds(cell, state.width, state.height)
    )


def _evaluate(state: State, snake_id: SnakeId) -> tuple[ActionEvaluation, ...]:
    me = state.snake(snake_id)
    bodies = body_cells(state)
    opp_heads = _opponent_next_heads(state, snake_id)

    landings: list[tuple[Action, Cell, frozenset[Cell]]] = []
    for action in ACTIONS:
        landing, _ = next_head(me.head, me.direction, action)
        occ = next_occupancy(state, snake_id, action, bodies=bodies)
        landings.append((action, landing, occ))

    # One shared blocked set for the BFS: the occupancies differ only in the
    # own tail, which stays solid exactly for the action that eats — and that
    # action's distance is 0, so it never consults the BFS (BR-EXP-5b).
    shared = next(
        (occ for _, landing, occ in landings if landing != state.food),
        landings[0][2],
    )
    dist = _food_distances(state, shared | state.obstacles)

    evaluations: list[ActionEvaluation] = []
    for action, landing, occ in landings:
        fatal = (
            not in_bounds(landing, state.width, state.height)
            or landing in state.obstacles
            or landing in occ
        )
        food_distance = 0 if landing == state.food else _lookup(state, dist, landing)
        evaluations.append(
            ActionEvaluation(
                action=action,
                landing=landing,
                occupancy=occ,
                fatal=fatal,
                head_risk=landing in opp_heads,
                flood=flood_fill_count(state, landing, occupancy=occ, limit=_FLOOD_LIMIT),
                food_distance=food_distance,
            )
        )
    return tuple(evaluations)


def _rank_key(evaluation: ActionEvaluation) -> tuple[int, int, int]:
    """Smallest food distance (unreachable last), then largest flood."""
    unreachable = evaluation.food_distance is None
    distance = 0 if evaluation.food_distance is None else evaluation.food_distance
    return (int(unreachable), distance, -evaluation.flood)


def _space_key(evaluation: ActionEvaluation) -> tuple[int, int, int]:
    return (0, 0, -evaluation.flood)


def _resolve(
    state: State,
    snake_id: SnakeId,
    candidates: list[ActionEvaluation],
    key: Callable[[ActionEvaluation], tuple[int, int, int]],
) -> tuple[Action, bool]:
    """Pick the best candidate; a left/right tie costs one draw (BR-EXP-11)."""
    best = min(key(e) for e in candidates)
    tied = [e for e in candidates if key(e) == best]
    for evaluation in tied:
        if evaluation.action is Action.straight:
            return Action.straight, False
    if len(tied) == 1:
        return tied[0].action, False
    # Only here is the RNG built, so the common path pays nothing (D46 item 8).
    rng = agent_generator(state.seed, state.tick, snake_index(snake_id))
    return tied[int(rng.integers(len(tied)))].action, True


def _decide(state: State, snake_id: SnakeId) -> ExpertDecision:
    ensure_playable(state, snake_id)
    me = state.snake(snake_id)
    opp = state.opponent(snake_id)
    evaluations = _evaluate(state, snake_id)

    survivable = [e for e in evaluations if not e.fatal]
    if not survivable:
        return ExpertDecision(Action.straight, "all_fatal", False, evaluations)

    # A strictly longer snake survives a head swap, so the filter is skipped.
    if me.length > opp.length:
        safe = survivable
    else:
        safe = [e for e in survivable if not e.head_risk]

    roomy = [e for e in safe if e.flood > me.length]
    if roomy:
        action, drawn = _resolve(state, snake_id, roomy, _rank_key)
        return ExpertDecision(action, "ranked", drawn, evaluations)
    if safe:
        action, drawn = _resolve(state, snake_id, safe, _space_key)
        return ExpertDecision(action, "fallback_space", drawn, evaluations)
    action, drawn = _resolve(state, snake_id, survivable, _space_key)
    return ExpertDecision(action, "fallback_head_risk", drawn, evaluations)


class ExpertAgent:
    """Stateless and pure: the same state always yields the same action."""

    def act(self, state: State, snake_id: SnakeId) -> Action:
        return _decide(state, snake_id).action
