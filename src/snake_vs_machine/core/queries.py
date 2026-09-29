"""Pure occupancy and flood-fill queries (D29, D32, D33)."""

from __future__ import annotations

from collections import deque

from snake_vs_machine.core.state import (
    Action,
    Cell,
    SnakeId,
    State,
    in_bounds,
    neighbors4,
    next_head,
)


def body_cells(state: State) -> frozenset[Cell]:
    """All current body cells. Suggested reuse per step (D35)."""
    return frozenset(state.snake_a.body) | frozenset(state.snake_b.body)


def next_occupancy(
    state: State,
    snake_id: SnakeId,
    action: Action,
    opponent_action: Action | None = None,
    bodies: frozenset[Cell] | None = None,
) -> frozenset[Cell]:
    """Cells still solid this tick from `snake_id`'s point of view.

    Own tail uses the real `action`. Opponent tail uses the real
    `opponent_action` when given; otherwise D29 (solid if opponent head is
    4-adjacent to food). Always includes both current heads.
    """
    me = state.snake(snake_id)
    opp = state.opponent(snake_id)
    occ = set(bodies if bodies is not None else body_cells(state))
    my_next, _ = next_head(me.head, me.direction, action)
    if state.food is None or my_next != state.food:
        occ.discard(me.tail)
    if opponent_action is not None:
        opp_next, _ = next_head(opp.head, opp.direction, opponent_action)
        if state.food is None or opp_next != state.food:
            occ.discard(opp.tail)
    elif state.food is None or state.food not in neighbors4(opp.head):
        occ.discard(opp.tail)
    occ.add(me.head)
    occ.add(opp.head)
    return frozenset(occ)


def is_fatal(state: State, snake_id: SnakeId, action: Action) -> bool:
    """Deterministic death for this action (conservative occupancy).

    Fatal: out of board, obstacle, or next cell in next_occupancy without
    opponent_action (D29 tails; opponent current head is FATAL — D32).
    Same-cell head-to-head on a third cell is not is_fatal. A swap may still
    spare the larger snake in engine.step; this function does not predict that.
    """
    me = state.snake(snake_id)
    nxt, _ = next_head(me.head, me.direction, action)
    if not in_bounds(nxt, state.width, state.height):
        return True
    if nxt in state.obstacles:
        return True
    return nxt in next_occupancy(state, snake_id, action)


def reachable_cells(
    state: State,
    start: Cell,
    occupancy: frozenset[Cell] | None = None,
    limit: int = 200,
) -> frozenset[Cell]:
    """4-connected cells from `start`, cap `limit`. Food is walkable."""
    blocked = set(state.obstacles)
    if occupancy is None:
        blocked |= set(body_cells(state))
    else:
        blocked |= set(occupancy)
    if not in_bounds(start, state.width, state.height) or start in blocked:
        return frozenset()
    seen: set[Cell] = {start}
    queue: deque[Cell] = deque([start])
    while queue and len(seen) < limit:
        cell = queue.popleft()
        for nxt in neighbors4(cell):
            if (
                in_bounds(nxt, state.width, state.height)
                and nxt not in blocked
                and nxt not in seen
            ):
                seen.add(nxt)
                queue.append(nxt)
                if len(seen) >= limit:
                    break
    return frozenset(seen)


def flood_fill_count(
    state: State,
    start: Cell,
    occupancy: frozenset[Cell] | None = None,
    limit: int = 200,
) -> int:
    """Exactly min(reachable component size, limit). Order-independent (D39)."""
    return len(reachable_cells(state, start, occupancy=occupancy, limit=limit))
