"""Transform helpers (D41) then feature PBT from new_match + step (D38)."""

from __future__ import annotations

from dataclasses import replace

import pytest
from hypothesis import given
from hypothesis import strategies as st

from snake_vs_machine.core.engine import step
from snake_vs_machine.core.features import _blocked, _free_cell_count, extract_features
from snake_vs_machine.core.queries import is_fatal, next_occupancy
from snake_vs_machine.core.setup import new_match
from snake_vs_machine.core.state import (
    Action,
    Cell,
    CoreConfig,
    EndReason,
    SnakeId,
    next_head,
)
from tests.core.board_transforms import apply_n, transform_state

_ACTIONS = (Action.straight, Action.turn_left, Action.turn_right)
_MIRROR_PAIRS = ((1, 2), (4, 5), (7, 8), (10, 11), (17, 18))


def _swap_left_right(vec: tuple[object, ...]) -> tuple[object, ...]:
    items = list(vec)
    for left, right in _MIRROR_PAIRS:
        items[left], items[right] = items[right], items[left]
    return tuple(items)


def test_rot90_four_times_is_identity() -> None:
    state = new_match(CoreConfig(obstacle_count=4), seed=3)
    assert apply_n(state, "rot90", 4) == state


def test_mirrors_twice_are_identity() -> None:
    state = new_match(CoreConfig(obstacle_count=4), seed=3)
    assert apply_n(state, "mx", 2) == state
    assert apply_n(state, "my", 2) == state


def test_rot180_kickoff_swaps_spawn_bodies() -> None:
    state = new_match(CoreConfig(), seed=0)
    rotated = transform_state(state, "rot180")
    assert rotated.snake_a.body == state.snake_b.body
    assert rotated.snake_b.body == state.snake_a.body


@st.composite
def playing_state(draw: st.DrawFn) -> object:
    seed = draw(st.integers(min_value=0, max_value=50_000))
    obstacle_count = draw(st.integers(min_value=0, max_value=8))
    n = draw(st.integers(min_value=0, max_value=16))
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
    return state


@given(playing_state())
def test_p_feat_det_range_consistency(state: object) -> None:
    if state.end_reason is not None:
        return
    first = extract_features(state, SnakeId.A)
    assert first == extract_features(state, SnakeId.A)
    for slot, name_index in enumerate(first):
        if slot == 19:
            assert isinstance(name_index, int)
        elif slot in {0, 1, 2, 9, 10, 11, 12, 14, 16, 17, 18}:
            assert name_index in (0, 1)
        else:
            assert 0.0 <= float(name_index) <= 1.0
    for d in (0, 1, 2):
        danger = first[d]
        dist = first[3 + d]
        space = first[6 + d]
        assert (danger == 1) == (dist == 0)
        if danger == 1:
            assert space == 0


@given(playing_state())
def test_p_feat_free_cells_formula_matches_scan(state: object) -> None:
    """Arithmetic _free_cell_count equals the cell-by-cell oracle (D42)."""
    me = state.snake(SnakeId.A)
    opp = state.snake(SnakeId.B)
    bodies = frozenset(me.body) | frozenset(opp.body)
    scanned = sum(
        1
        for y in range(state.height)
        for x in range(state.width)
        if Cell(x, y) not in bodies and Cell(x, y) not in state.obstacles
    )
    assert _free_cell_count(state, me, opp) == scanned


@given(playing_state())
def test_p_feat_danger_matches_is_fatal(state: object) -> None:
    """The inlined _blocked danger equals is_fatal for every action (D43)."""
    if state.end_reason is not None:
        return
    for snake_id in (SnakeId.A, SnakeId.B):
        me = state.snake(snake_id)
        for action in _ACTIONS:
            landing, _ = next_head(me.head, me.direction, action)
            occ = next_occupancy(state, snake_id, action)
            assert _blocked(state, landing, occ) == is_fatal(state, snake_id, action)


@given(playing_state())
def test_p_feat_rot_mirror(state: object) -> None:
    if state.end_reason is not None:
        return
    base = extract_features(state, SnakeId.A)
    for kind in ("rot90", "rot180", "rot270"):
        assert extract_features(transform_state(state, kind), SnakeId.A) == base
    for kind in ("mx", "my"):
        assert extract_features(transform_state(state, kind), SnakeId.A) == _swap_left_right(base)


@given(playing_state())
def test_p_feat_dead(state: object) -> None:
    if state.end_reason is None:
        terminal = replace(state, end_reason=EndReason.timeout)
        with pytest.raises(ValueError):
            extract_features(terminal, SnakeId.A)
        return
    with pytest.raises(ValueError):
        extract_features(state, SnakeId.A)
