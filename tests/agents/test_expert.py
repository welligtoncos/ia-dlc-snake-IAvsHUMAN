"""ExpertAgent examples (BR-EXP-1..14, worked examples 1-3, D49 item 3)."""

from __future__ import annotations

from dataclasses import replace

import pytest

from snake_vs_machine.agents.expert import ExpertAgent, _decide
from snake_vs_machine.core.queries import is_fatal
from snake_vs_machine.core.setup import new_match
from snake_vs_machine.core.state import (
    Action,
    Cell,
    CoreConfig,
    Direction,
    EndReason,
    Snake,
    SnakeId,
    State,
)


def _kickoff(seed: int = 0) -> State:
    return new_match(CoreConfig(), seed=seed)


def test_worked_example_1_golden_kickoff() -> None:
    """The U3 golden, manually checked in D49 item 3.

    Open board, so the BFS distance equals the Manhattan distance: 14 ahead,
    16 to the left, 14 to the right. Floods tie at the 200 cap, so the final
    tie-break is the `straight` preference.
    """
    state = _kickoff()
    assert state.food == Cell(10, 9)
    assert state.snake_a.head == Cell(2, 2)
    assert state.snake_a.direction is Direction.E

    decision = _decide(state, SnakeId.A)
    by_action = {e.action: e for e in decision.evaluations}

    assert by_action[Action.straight].landing == Cell(3, 2)
    assert by_action[Action.turn_left].landing == Cell(2, 1)
    assert by_action[Action.turn_right].landing == Cell(2, 3)

    assert by_action[Action.straight].food_distance == 14
    assert by_action[Action.turn_left].food_distance == 16
    assert by_action[Action.turn_right].food_distance == 14

    assert all(not e.fatal for e in decision.evaluations)
    assert all(not e.head_risk for e in decision.evaluations)
    assert {e.flood for e in decision.evaluations} == {200}

    assert decision.action is Action.straight
    assert decision.stage == "ranked"
    assert decision.drawn is False
    assert ExpertAgent().act(state, SnakeId.A) is Action.straight


def _head_risk_state(opponent_length: int) -> State:
    """A faces east into a cell that B could also occupy next tick.

    A head (5,5) facing east, body of 4. B head (7,5) facing west, so its
    possible next heads are (6,5), (7,6) and (7,4) — and (6,5) is exactly
    where A's `straight` lands. Food at (6,9) makes `straight` and
    `turn_right` tie on distance 4, with `turn_left` at 6.
    """
    state = _kickoff()
    snake_a = Snake(
        id=SnakeId.A,
        body=(Cell(5, 5), Cell(4, 5), Cell(3, 5), Cell(2, 5)),
        direction=Direction.E,
    )
    b_body = tuple(Cell(7 + i, 5) for i in range(opponent_length))
    snake_b = Snake(id=SnakeId.B, body=b_body, direction=Direction.W)
    return replace(state, snake_a=snake_a, snake_b=snake_b, food=Cell(6, 9))


def test_worked_example_2_head_risk_waived_when_strictly_longer() -> None:
    state = _head_risk_state(opponent_length=3)
    assert state.snake_a.length > state.snake_b.length

    decision = _decide(state, SnakeId.A)
    straight = next(e for e in decision.evaluations if e.action is Action.straight)
    assert straight.landing == Cell(6, 5)
    assert straight.head_risk is True

    # The filter is skipped, so the contested cell stays a candidate and wins.
    assert decision.action is Action.straight
    assert decision.stage == "ranked"


def test_worked_example_2_companion_head_risk_applies_at_equal_length() -> None:
    state = _head_risk_state(opponent_length=4)
    assert state.snake_a.length == state.snake_b.length

    decision = _decide(state, SnakeId.A)
    straight = next(e for e in decision.evaluations if e.action is Action.straight)
    assert straight.head_risk is True

    # Same board, different action: the contested cell is now excluded.
    assert decision.action is Action.turn_right
    assert decision.stage == "ranked"


def _all_fatal_state() -> State:
    """A at the top-right corner facing east, with the only exit blocked."""
    state = _kickoff()
    snake_a = Snake(
        id=SnakeId.A,
        body=(Cell(19, 0), Cell(18, 0), Cell(17, 0)),
        direction=Direction.E,
    )
    return replace(state, snake_a=snake_a, obstacles=frozenset({Cell(19, 1)}))


def test_all_fatal_returns_straight() -> None:
    state = _all_fatal_state()
    assert all(is_fatal(state, SnakeId.A, a) for a in (
        Action.straight,
        Action.turn_left,
        Action.turn_right,
    ))

    decision = _decide(state, SnakeId.A)
    assert decision.action is Action.straight
    assert decision.stage == "all_fatal"
    assert decision.drawn is False


def _left_right_tie_state() -> State:
    """`straight` is walled off and the two turns are symmetric about y = 5."""
    state = _kickoff()
    snake_a = Snake(
        id=SnakeId.A,
        body=(Cell(5, 5), Cell(4, 5), Cell(3, 5)),
        direction=Direction.E,
    )
    return replace(state, snake_a=snake_a, obstacles=frozenset({Cell(6, 5)}), food=Cell(10, 5))


def test_left_right_tie_is_resolved_by_a_draw() -> None:
    state = _left_right_tie_state()
    decision = _decide(state, SnakeId.A)

    assert decision.drawn is True
    assert decision.action in (Action.turn_left, Action.turn_right)
    assert decision.stage == "ranked"


def test_decision_is_deterministic_including_the_draw() -> None:
    state = _left_right_tie_state()
    assert _decide(state, SnakeId.A).action is _decide(state, SnakeId.A).action


def _walled_state(free: set[Cell], snake_a: Snake, snake_b: Snake, food: Cell) -> State:
    """Everything outside `free` is an obstacle."""
    state = _kickoff()
    keep = free | set(snake_a.body) | set(snake_b.body) | {food}
    obstacles = frozenset(
        Cell(x, y)
        for y in range(state.height)
        for x in range(state.width)
        if Cell(x, y) not in keep
    )
    return replace(
        state,
        snake_a=snake_a,
        snake_b=snake_b,
        food=food,
        obstacles=obstacles,
    )


def test_worked_example_3_space_fallback() -> None:
    """Every survivable action leads into a pocket smaller than the body.

    `straight` reaches a dead end of 1 cell, `turn_left` is a wall, and
    `turn_right` opens a corridor of 3. With a body of 3, nothing satisfies
    `flood > length`, so the decision falls back to the roomiest move.
    """
    snake_a = Snake(
        id=SnakeId.A,
        body=(Cell(5, 5), Cell(4, 5), Cell(3, 5)),
        direction=Direction.E,
    )
    snake_b = Snake(
        id=SnakeId.B,
        body=(Cell(17, 17), Cell(18, 17), Cell(19, 17)),
        direction=Direction.W,
    )
    free = {Cell(6, 5), Cell(5, 6), Cell(5, 7), Cell(5, 8)}
    state = _walled_state(free, snake_a, snake_b, food=Cell(16, 17))

    decision = _decide(state, SnakeId.A)
    by_action = {e.action: e for e in decision.evaluations}

    assert by_action[Action.turn_left].fatal is True
    assert by_action[Action.straight].flood == 1
    assert by_action[Action.turn_right].flood == 3
    assert all(e.flood <= snake_a.length for e in decision.evaluations if not e.fatal)

    assert decision.action is Action.turn_right
    assert decision.stage == "fallback_space"
    assert decision.drawn is False


def test_head_risk_fallback_when_every_safe_action_is_contested() -> None:
    """S2 empties out, so the decision falls back to S1 (BR-EXP-12)."""
    state = _kickoff()
    snake_a = Snake(
        id=SnakeId.A,
        body=(Cell(5, 5), Cell(4, 5), Cell(3, 5)),
        direction=Direction.E,
    )
    snake_b = Snake(
        id=SnakeId.B,
        body=(Cell(7, 5), Cell(8, 5), Cell(9, 5)),
        direction=Direction.W,
    )
    state = replace(
        state,
        snake_a=snake_a,
        snake_b=snake_b,
        obstacles=frozenset({Cell(5, 4), Cell(5, 6)}),
    )
    assert snake_a.length == snake_b.length

    decision = _decide(state, SnakeId.A)
    by_action = {e.action: e for e in decision.evaluations}
    assert by_action[Action.turn_left].fatal is True
    assert by_action[Action.turn_right].fatal is True
    assert by_action[Action.straight].head_risk is True

    assert decision.action is Action.straight
    assert decision.stage == "fallback_head_risk"


def test_never_picks_a_fatal_action_when_one_is_safe() -> None:
    for seed in range(15):
        state = _kickoff(seed=seed)
        chosen = ExpertAgent().act(state, SnakeId.A)
        assert not is_fatal(state, SnakeId.A, chosen)


def test_food_distance_is_none_when_there_is_no_food() -> None:
    state = replace(_kickoff(), food=None)
    decision = _decide(state, SnakeId.A)
    assert all(e.food_distance is None for e in decision.evaluations)


def test_rejects_terminal_state() -> None:
    state = replace(_kickoff(), end_reason=EndReason.timeout)
    with pytest.raises(ValueError, match="terminal"):
        ExpertAgent().act(state, SnakeId.A)


def test_rejects_dead_snake() -> None:
    state = _kickoff()
    state = replace(state, snake_a=replace(state.snake_a, alive=False))
    with pytest.raises(ValueError, match="dead snake A"):
        ExpertAgent().act(state, SnakeId.A)
