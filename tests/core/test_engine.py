"""Example tests for rules 1–10, lifecycle, replay identity (D36)."""

from __future__ import annotations

from dataclasses import replace

import pytest

from snake_vs_machine.core.engine import is_terminal, outcome, step
from snake_vs_machine.core.setup import new_match
from snake_vs_machine.core.state import (
    Action,
    Cell,
    CoreConfig,
    DeathCause,
    Direction,
    EndReason,
    Outcome,
    copy,
)
from tests.core.test_engine_critical import _place


def test_br_s1_s2_kickoff_templates() -> None:
    state = new_match(CoreConfig(), seed=0)
    assert state.snake_a.body == (Cell(2, 2), Cell(1, 2), Cell(0, 2))
    assert state.snake_a.direction is Direction.E
    assert state.snake_a.length == 3
    assert state.snake_b.body == (Cell(17, 17), Cell(18, 17), Cell(19, 17))
    assert state.snake_b.direction is Direction.W
    assert state.max_ticks == 1800
    assert state.tick == 0
    assert state.end_reason is None
    assert not is_terminal(state)


def test_br_l2_terminal_step_is_identity_snapshot() -> None:
    state = _place(
        a_body=(Cell(0, 5), Cell(1, 5), Cell(2, 5)),
        a_dir=Direction.W,
        b_body=(Cell(19, 5), Cell(18, 5), Cell(17, 5)),
        b_dir=Direction.E,
        food=Cell(10, 9),
    )
    dead = step(state, Action.straight, Action.straight)
    assert is_terminal(dead)
    again = step(dead, Action.turn_left, Action.turn_right)
    assert again == dead
    assert again.tick == dead.tick
    assert again is not dead


def test_step_does_not_mutate_input() -> None:
    state = new_match(CoreConfig(), seed=4)
    before = copy(state)
    step(state, Action.straight, Action.straight)
    assert state == before


def test_wall_kills_a_b_survives() -> None:
    state = _place(
        a_body=(Cell(0, 5), Cell(1, 5), Cell(2, 5)),
        a_dir=Direction.W,
        b_body=(Cell(10, 10), Cell(11, 10), Cell(12, 10)),
        b_dir=Direction.W,
        food=Cell(3, 3),
    )
    nxt = step(state, Action.straight, Action.straight)
    assert not nxt.snake_a.alive
    assert nxt.snake_a.death_cause is DeathCause.wall
    assert nxt.snake_b.alive
    assert nxt.end_reason is EndReason.death
    assert outcome(nxt) is Outcome.win_b


def test_obstacle_kills_entering_snake() -> None:
    base = new_match(CoreConfig(), seed=0)
    state = replace(base, obstacles=frozenset({Cell(3, 2)}))
    nxt = step(state, Action.straight, Action.straight)
    assert not nxt.snake_a.alive
    assert nxt.snake_a.death_cause is DeathCause.obstacle
    assert nxt.snake_b.alive
    assert nxt.obstacles == state.obstacles


def test_self_body() -> None:
    """A faces its own neck (4,5); tail is (3,6) and does not vacate that cell."""
    state = _place(
        a_body=(Cell(5, 5), Cell(4, 5), Cell(3, 5), Cell(3, 6)),
        a_dir=Direction.W,
        b_body=(Cell(15, 15), Cell(16, 15), Cell(17, 15)),
        b_dir=Direction.W,
        food=Cell(1, 1),
    )
    nxt = step(state, Action.straight, Action.straight)
    assert not nxt.snake_a.alive
    assert nxt.snake_a.death_cause is DeathCause.self_body
    assert nxt.snake_b.alive


def test_follow_own_vacating_tail() -> None:
    state = _place(
        a_body=(Cell(5, 5), Cell(4, 5), Cell(4, 6), Cell(5, 6)),
        a_dir=Direction.E,
        b_body=(Cell(15, 15), Cell(16, 15), Cell(17, 15)),
        b_dir=Direction.W,
        food=Cell(1, 1),
    )
    nxt = step(state, Action.turn_right, Action.straight)
    # turn_right from E → S → (5, 6) which is the tail; food is not (5, 6).
    # Wait: this is the same geometry as self_body — tail IS (5,6).
    # If not eating, tail vacates so A should SURVIVE. The previous test used
    # the same geometry expecting self_body — that would be wrong.
    #
    # body (5,5),(4,5),(4,6),(5,6); turn_right → (5,6) = tail.
    # Occupancy discards own tail when not eating → not self_body.
    assert nxt.snake_a.alive
    assert nxt.snake_a.head == Cell(5, 6)


def test_own_tail_solid_when_eating() -> None:
    state = _place(
        a_body=(Cell(5, 5), Cell(4, 5), Cell(4, 6), Cell(5, 6)),
        a_dir=Direction.E,
        b_body=(Cell(15, 15), Cell(16, 15), Cell(17, 15)),
        b_dir=Direction.W,
        food=Cell(5, 6),
    )
    nxt = step(state, Action.turn_right, Action.straight)
    assert not nxt.snake_a.alive
    assert nxt.snake_a.death_cause is DeathCause.self_body


def test_h2h_unequal_larger_survives_and_eats() -> None:
    food = Cell(10, 9)
    state = _place(
        a_body=(Cell(9, 9), Cell(8, 9), Cell(7, 9), Cell(6, 9)),
        a_dir=Direction.E,
        b_body=(Cell(11, 9), Cell(12, 9), Cell(13, 9)),
        b_dir=Direction.W,
        food=food,
    )
    nxt = step(state, Action.straight, Action.straight)
    assert nxt.snake_a.alive
    assert nxt.snake_a.length == 5
    assert not nxt.snake_b.alive
    assert nxt.snake_b.death_cause is DeathCause.head_to_head
    assert nxt.food != food
    assert outcome(nxt) is Outcome.win_a


def test_h2h_exactly_one_candidate_survives() -> None:
    """Swap onto B's head, which is an obstacle: A dies obstacle; B is the only H2H candidate."""
    state = replace(
        _place(
            a_body=(Cell(5, 5), Cell(4, 5), Cell(3, 5)),
            a_dir=Direction.E,
            b_body=(Cell(6, 5), Cell(7, 5), Cell(8, 5)),
            b_dir=Direction.W,
            food=Cell(10, 9),
        ),
        obstacles=frozenset({Cell(6, 5)}),
    )
    nxt = step(state, Action.straight, Action.straight)
    assert not nxt.snake_a.alive
    assert nxt.snake_a.death_cause is DeathCause.obstacle
    assert nxt.snake_b.alive
    assert nxt.snake_b.head == Cell(5, 5)
    assert nxt.snake_b.death_cause is None


def test_timeout_equal_length_draw() -> None:
    state = replace(new_match(CoreConfig(), seed=0), max_ticks=1)
    nxt = step(state, Action.straight, Action.straight)
    assert nxt.snake_a.alive
    assert nxt.snake_b.alive
    assert nxt.snake_a.death_cause is None
    assert nxt.snake_b.death_cause is None
    assert nxt.end_reason is EndReason.timeout
    assert nxt.tick == 1
    assert is_terminal(nxt)
    assert outcome(nxt) is Outcome.draw


def test_timeout_longer_body_wins() -> None:
    base = replace(new_match(CoreConfig(), seed=0), max_ticks=1)
    longer = replace(base.snake_a, body=base.snake_a.body + (Cell(0, 3),))
    state = replace(base, snake_a=longer)
    nxt = step(state, Action.turn_left, Action.turn_left)
    assert nxt.end_reason is EndReason.timeout
    assert outcome(nxt) is Outcome.win_a


def test_outcome_undefined_while_playing() -> None:
    state = new_match(CoreConfig(), seed=0)
    with pytest.raises(ValueError, match="undefined"):
        outcome(state)


def test_surviving_eat_respawns_food() -> None:
    food = Cell(10, 9)
    state = _place(
        a_body=(Cell(9, 9), Cell(8, 9), Cell(7, 9)),
        a_dir=Direction.E,
        b_body=(Cell(17, 17), Cell(18, 17), Cell(19, 17)),
        b_dir=Direction.W,
        food=food,
    )
    nxt = step(state, Action.straight, Action.straight)
    assert nxt.snake_a.alive
    assert nxt.snake_a.length == 4
    assert nxt.food is not None
    assert nxt.food != food
    assert nxt.food not in nxt.snake_a.body
    assert nxt.food not in nxt.snake_b.body
    assert nxt.food not in nxt.obstacles


def test_food_none_when_board_full_after_eat() -> None:
    base = new_match(CoreConfig(), seed=0)
    food = Cell(3, 2)
    all_cells = {Cell(x, y) for y in range(base.height) for x in range(base.width)}
    bodies = set(base.snake_a.body) | set(base.snake_b.body)
    obstacles = frozenset(all_cells - bodies - {food})
    state = replace(base, food=food, obstacles=obstacles)
    nxt = step(state, Action.straight, Action.straight)
    assert nxt.snake_a.alive
    assert nxt.food is None


def test_replay_identity_includes_food_respawn() -> None:
    food = Cell(10, 9)
    seq = (
        (Action.straight, Action.straight),
        (Action.straight, Action.turn_left),
        (Action.turn_right, Action.straight),
    )
    first = _place(
        a_body=(Cell(9, 9), Cell(8, 9), Cell(7, 9)),
        a_dir=Direction.E,
        b_body=(Cell(17, 17), Cell(18, 17), Cell(19, 17)),
        b_dir=Direction.W,
        food=food,
    )
    second = _place(
        a_body=(Cell(9, 9), Cell(8, 9), Cell(7, 9)),
        a_dir=Direction.E,
        b_body=(Cell(17, 17), Cell(18, 17), Cell(19, 17)),
        b_dir=Direction.W,
        food=food,
    )
    for action_a, action_b in seq:
        first = step(first, action_a, action_b)
        second = step(second, action_a, action_b)
        assert first == second
    assert first.food != food


def test_replay_identity_from_new_match() -> None:
    cfg = CoreConfig(obstacle_count=4)
    seed = 123
    actions = [
        (Action.straight, Action.straight),
        (Action.turn_left, Action.turn_right),
        (Action.straight, Action.turn_left),
        (Action.turn_right, Action.straight),
        (Action.straight, Action.straight),
    ]
    left = new_match(cfg, seed)
    right = new_match(cfg, seed)
    for action_a, action_b in actions:
        if left.end_reason is not None:
            break
        left = step(left, action_a, action_b)
        right = step(right, action_a, action_b)
        assert left == right
