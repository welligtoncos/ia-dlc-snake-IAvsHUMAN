"""Property-based tests for U3 agents (D44, D46, D49)."""

from __future__ import annotations

from collections import deque
from dataclasses import replace

from hypothesis import given
from hypothesis import strategies as st

from snake_vs_machine.agents.base import ACTIONS
from snake_vs_machine.agents.expert import ExpertAgent, _decide, _food_distances, _lookup
from snake_vs_machine.agents.human import HumanAgent
from snake_vs_machine.agents.random_agent import RandomAgent
from snake_vs_machine.core.queries import is_fatal, next_occupancy
from snake_vs_machine.core.setup import new_match
from snake_vs_machine.core.state import (
    Action,
    Cell,
    CoreConfig,
    Direction,
    SnakeId,
    apply_action,
    copy,
    in_bounds,
    neighbors4,
    next_head,
)
from tests.core.board_transforms import transform_state
from tests.core.test_features_pbt import playing_state

_MIRROR_ACTION = {
    Action.straight: Action.straight,
    Action.turn_left: Action.turn_right,
    Action.turn_right: Action.turn_left,
}


def _reverse(direction: Direction) -> Direction:
    return apply_action(apply_action(direction, Action.turn_left), Action.turn_left)


def _oracle_distance(state: object, landing: Cell, occupancy: frozenset[Cell]) -> int | None:
    food = state.food
    if food is None:
        return None
    if landing == food:
        return 0
    if not in_bounds(landing, state.width, state.height):
        return None
    blocked = occupancy | state.obstacles
    if landing in blocked:
        return None
    seen = {landing}
    queue: deque[tuple[Cell, int]] = deque([(landing, 0)])
    while queue:
        cell, dist = queue.popleft()
        if cell == food:
            return dist
        for nxt in neighbors4(cell):
            if nxt in seen or not in_bounds(nxt, state.width, state.height):
                continue
            if nxt in blocked and nxt != food:
                continue
            seen.add(nxt)
            queue.append((nxt, dist + 1))
    return None


@given(playing_state(), st.sampled_from(list(SnakeId)))
def test_p_agt_action_pure_frozen(state: object, snake_id: SnakeId) -> None:
    if state.end_reason is not None or not state.snake(snake_id).alive:
        return
    before = copy(state)
    for agent in (RandomAgent(), ExpertAgent()):
        action = agent.act(state, snake_id)
        assert action in ACTIONS
        assert agent.act(state, snake_id) is action
        assert state == before


@given(playing_state(), st.sampled_from(list(SnakeId)))
def test_p_rnd_safe(state: object, snake_id: SnakeId) -> None:
    if state.end_reason is not None or not state.snake(snake_id).alive:
        return
    safe = [a for a in ACTIONS if not is_fatal(state, snake_id, a)]
    if not safe:
        return
    assert RandomAgent().act(state, snake_id) in safe


@given(st.integers(min_value=0, max_value=50_000))
def test_p_rnd_spread(start: int) -> None:
    seen: set[Action] = set()
    for seed in range(start, start + 50):
        state = new_match(CoreConfig(max_ticks=60), seed=seed)
        seen.add(RandomAgent().act(state, SnakeId.A))
    assert seen == set(ACTIONS)


@given(playing_state(), st.sampled_from(list(SnakeId)))
def test_p_exp_safe_space_headrisk_det(state: object, snake_id: SnakeId) -> None:
    if state.end_reason is not None or not state.snake(snake_id).alive:
        return
    decision = _decide(state, snake_id)
    me = state.snake(snake_id)
    opp = state.opponent(snake_id)
    by_action = {e.action: e for e in decision.evaluations}
    chosen = by_action[decision.action]

    if any(not e.fatal for e in decision.evaluations):
        assert not chosen.fatal
    if decision.stage == "ranked":
        assert chosen.flood > me.length
        if me.length <= opp.length:
            assert not chosen.head_risk
    assert _decide(state, snake_id).action is decision.action
    assert ExpertAgent().act(state, snake_id) is decision.action


@given(
    playing_state(),
    st.sampled_from(list(SnakeId)),
    st.sampled_from(("rot90", "rot180", "rot270")),
)
def test_p_exp_rot(state: object, snake_id: SnakeId, kind: str) -> None:
    if state.end_reason is not None or not state.snake(snake_id).alive:
        return
    decision = _decide(state, snake_id)
    if decision.drawn:
        return
    rotated = transform_state(state, kind)
    rotated_decision = _decide(rotated, snake_id)
    if rotated_decision.drawn:
        return
    assert rotated_decision.action is decision.action


@given(
    playing_state(),
    st.sampled_from(list(SnakeId)),
    st.sampled_from(("mx", "my")),
)
def test_p_exp_mirror(state: object, snake_id: SnakeId, kind: str) -> None:
    """P-EXP-MIRROR (D49 item 2): a mirror swaps left/right and keeps straight."""
    if state.end_reason is not None or not state.snake(snake_id).alive:
        return
    decision = _decide(state, snake_id)
    if decision.drawn:
        return
    mirrored = transform_state(state, kind)
    mirrored_decision = _decide(mirrored, snake_id)
    if mirrored_decision.drawn:
        return
    assert mirrored_decision.action is _MIRROR_ACTION[decision.action]


@given(playing_state(), st.sampled_from(list(SnakeId)))
def test_p_exp_dist(state: object, snake_id: SnakeId) -> None:
    """P-EXP-DIST: one BFS from the food matches a per-landing BFS (Etapa 12)."""
    if state.end_reason is not None or not state.snake(snake_id).alive:
        return
    me = state.snake(snake_id)
    shared = None
    for action in ACTIONS:
        landing, _ = next_head(me.head, me.direction, action)
        if landing != state.food:
            shared = next_occupancy(state, snake_id, action)
            break
    if shared is None:
        shared = next_occupancy(state, snake_id, Action.straight)
    dist = _food_distances(state, shared | state.obstacles)

    for action in ACTIONS:
        if is_fatal(state, snake_id, action):
            continue
        landing, _ = next_head(me.head, me.direction, action)
        occ = next_occupancy(state, snake_id, action)
        expected = 0 if landing == state.food else _lookup(state, dist, landing)
        assert expected == _oracle_distance(state, landing, occ)


@given(st.lists(st.sampled_from(list(Direction)), min_size=0, max_size=12))
def test_p_hum_buffer_invariants(commands: list[Direction]) -> None:
    state = new_match(CoreConfig(max_ticks=60), seed=0)
    agent = HumanAgent()
    facing = state.snake_a.direction
    agent.act(state, SnakeId.A)

    for command in commands:
        before = agent.pending()
        agent.push_absolute(command)
        after = agent.pending()
        assert len(after) <= 2
        if len(before) == 2:
            assert after == before
        pending = agent.pending()
        for previous, current in zip(pending, pending[1:], strict=False):
            assert current is not previous
            assert current is not _reverse(previous)

    drained = 0
    while agent.pending():
        before_len = len(agent.pending())
        facing_state = replace(state, snake_a=replace(state.snake_a, direction=facing))
        action = agent.act(facing_state, SnakeId.A)
        assert action in ACTIONS
        assert apply_action(facing, action) is not _reverse(facing)
        assert len(agent.pending()) == before_len - 1
        facing = apply_action(facing, action)
        drained += 1

    empty_len = len(agent.pending())
    agent.act(replace(state, snake_a=replace(state.snake_a, direction=facing)), SnakeId.A)
    assert len(agent.pending()) == empty_len
    assert drained <= 2
