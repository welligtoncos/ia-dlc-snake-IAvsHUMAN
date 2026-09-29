"""PBT from new_match + step only (D36). Never hand-build State."""

from __future__ import annotations

from hypothesis import given
from hypothesis import strategies as st

from snake_vs_machine.core.engine import is_terminal, outcome, step
from snake_vs_machine.core.queries import is_fatal, next_occupancy
from snake_vs_machine.core.setup import _chebyshev_disk, _free_connected, new_match
from snake_vs_machine.core.state import (
    Action,
    Cell,
    CoreConfig,
    DeathCause,
    Side,
    SnakeId,
    copy,
)

_ACTIONS = (Action.straight, Action.turn_left, Action.turn_right)
_BODY_CAUSES = (
    DeathCause.wall,
    DeathCause.obstacle,
    DeathCause.self_body,
    DeathCause.opponent_body,
)


def _rot180(cell: Cell, width: int, height: int) -> Cell:
    return Cell(width - 1 - cell.x, height - 1 - cell.y)


@st.composite
def constructed_play(draw: st.DrawFn) -> tuple[object, list[tuple[Action, Action]]]:
    seed = draw(st.integers(min_value=0, max_value=50_000))
    obstacle_count = draw(st.integers(min_value=0, max_value=8))
    n = draw(st.integers(min_value=0, max_value=20))
    actions = draw(
        st.lists(
            st.tuples(st.sampled_from(_ACTIONS), st.sampled_from(_ACTIONS)),
            min_size=n,
            max_size=n,
        )
    )
    state = new_match(CoreConfig(obstacle_count=obstacle_count), seed=seed)
    for action_a, action_b in actions:
        if state.end_reason is not None:
            break
        state = step(state, action_a, action_b)
    extra = draw(st.tuples(st.sampled_from(_ACTIONS), st.sampled_from(_ACTIONS)))
    return state, extra


@st.composite
def kickoff(draw: st.DrawFn) -> object:
    seed = draw(st.integers(min_value=0, max_value=50_000))
    obstacle_count = draw(st.integers(min_value=0, max_value=8))
    return new_match(CoreConfig(obstacle_count=obstacle_count), seed=seed)


@given(kickoff())
def test_p_copy(state: object) -> None:
    cloned = copy(state)
    assert cloned == state
    assert hash(cloned) == hash(state)


@given(constructed_play())
def test_p_fatal(data: tuple[object, tuple[Action, Action]]) -> None:
    state, _ = data
    if state.end_reason is not None:
        return
    for snake_id in (SnakeId.A, SnakeId.B):
        for action in _ACTIONS:
            if is_fatal(state, snake_id, action):
                continue
            for opponent_action in _ACTIONS:
                action_a = action if snake_id is SnakeId.A else opponent_action
                action_b = opponent_action if snake_id is SnakeId.A else action
                nxt = step(state, action_a, action_b)
                assert nxt.snake(snake_id).death_cause not in _BODY_CAUSES


@given(constructed_play())
def test_p_occ(data: tuple[object, tuple[Action, Action]]) -> None:
    state, extra = data
    if state.end_reason is not None:
        return
    action_a, action_b = extra
    nxt = step(state, action_a, action_b)
    for snake_id, action, opponent_action in (
        (SnakeId.A, action_a, action_b),
        (SnakeId.B, action_b, action_a),
    ):
        snake = nxt.snake(snake_id)
        if not snake.alive:
            continue
        leftovers = set(snake.body[1:])
        occ = next_occupancy(state, snake_id, action, opponent_action)
        pre = set(state.snake(snake_id).body)
        assert leftovers == occ & pre


@given(constructed_play())
def test_p_occ_conserv(data: tuple[object, tuple[Action, Action]]) -> None:
    state, extra = data
    action_a, action_b = extra
    for snake_id, action, opponent_action in (
        (SnakeId.A, action_a, action_b),
        (SnakeId.B, action_b, action_a),
    ):
        conservative = next_occupancy(state, snake_id, action)
        real = next_occupancy(state, snake_id, action, opponent_action)
        assert conservative >= real


@given(constructed_play())
def test_p_eng_invariants(data: tuple[object, tuple[Action, Action]]) -> None:
    state, extra = data
    if state.end_reason is not None:
        nxt = step(state, extra[0], extra[1])
        assert nxt == state
        return
    action_a, action_b = extra
    nxt = step(state, action_a, action_b)
    living: list[Cell] = []
    if nxt.snake_a.alive:
        assert nxt.snake_a.length >= 3
        living.extend(nxt.snake_a.body)
    if nxt.snake_b.alive:
        assert nxt.snake_b.length >= 3
        living.extend(nxt.snake_b.body)
    assert len(living) == len(set(living))
    assert nxt.obstacles == state.obstacles
    foods = [nxt.food] if nxt.food is not None else []
    assert len(foods) <= 1
    if nxt.snake_a.alive and nxt.snake_b.alive and state.food is not None:
        assert nxt.food is not None or (
            set(nxt.snake_a.body) | set(nxt.snake_b.body) | set(nxt.obstacles)
        ) == {Cell(x, y) for y in range(nxt.height) for x in range(nxt.width)}
    if is_terminal(nxt):
        result = outcome(nxt)
        assert result in (result.__class__.win_a, result.__class__.win_b, result.__class__.draw)
        winners = [result.name.startswith("win")]
        assert sum(1 for flag in winners if flag) <= 1


@given(kickoff())
def test_p_setup_sym_conn_zone_det(state: object) -> None:
    for cell in state.obstacles:
        assert _rot180(cell, state.width, state.height) in state.obstacles
    bodies = frozenset(state.snake_a.body + state.snake_b.body)
    assert _free_connected(state.width, state.height, state.obstacles, bodies)
    forbidden = set(_chebyshev_disk(state.snake_a.head))
    forbidden |= _chebyshev_disk(state.snake_b.head)
    ahead_a = Cell(3, 2) if state.side_a is Side.NW else Cell(16, 17)
    ahead_b = Cell(3, 2) if state.side_b is Side.NW else Cell(16, 17)
    forbidden |= _chebyshev_disk(ahead_a)
    forbidden |= _chebyshev_disk(ahead_b)
    forbidden.update(state.snake_a.body)
    forbidden.update(state.snake_b.body)
    if state.food is not None:
        forbidden.add(state.food)
    assert state.obstacles.isdisjoint(forbidden)
    again = new_match(
        CoreConfig(obstacle_count=len(state.obstacles), width=state.width, height=state.height),
        seed=state.seed,
    )
    assert again == new_match(
        CoreConfig(obstacle_count=len(state.obstacles), width=state.width, height=state.height),
        seed=state.seed,
    )
