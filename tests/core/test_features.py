"""Example tests for extract_features (D38–D39). Written before features.py (TDD)."""

from __future__ import annotations

from dataclasses import replace

import pytest

from snake_vs_machine.core.engine import step
from snake_vs_machine.core.features import (
    FEATURE_SCHEMA_VERSION,
    extract_features,
    feature_names,
)
from snake_vs_machine.core.setup import new_match
from snake_vs_machine.core.state import (
    Action,
    Cell,
    CoreConfig,
    Direction,
    EndReason,
    SnakeId,
)
from tests.core.test_engine_critical import _place

GOLDEN_A = (
    0,
    0,
    0,
    0.85,
    0.10,
    0.85,
    1.0,
    1.0,
    1.0,
    1,
    0,
    1,
    0,
    15 / 38,
    0,
    30 / 38,
    0,
    0,
    0,
    0,
)


def test_feature_names_length_and_order() -> None:
    names = feature_names()
    assert FEATURE_SCHEMA_VERSION == 1
    assert len(names) == 20
    assert names[0] == "danger_ahead"
    assert names[19] == "length_diff"


def test_golden_vector_kickoff_snake_a() -> None:
    state = new_match(CoreConfig(), seed=0)
    vec = extract_features(state, SnakeId.A)
    assert len(vec) == 20
    for i, (got, exp) in enumerate(zip(vec, GOLDEN_A, strict=True)):
        if i == 19:
            assert got == exp
        else:
            assert got == pytest.approx(exp), f"slot {i}"


def test_fairness_kickoff_a_equals_b() -> None:
    state = new_match(CoreConfig(), seed=0)
    assert extract_features(state, SnakeId.A) == extract_features(state, SnakeId.B)


def test_value_error_when_terminal() -> None:
    state = replace(new_match(CoreConfig(), seed=0), end_reason=EndReason.timeout)
    with pytest.raises(ValueError):
        extract_features(state, SnakeId.A)


def test_value_error_when_snake_dead() -> None:
    wall = _place(
        a_body=(Cell(0, 5), Cell(1, 5), Cell(2, 5)),
        a_dir=Direction.W,
        b_body=(Cell(10, 10), Cell(11, 10), Cell(12, 10)),
        b_dir=Direction.W,
        food=Cell(3, 3),
    )
    dead = step(wall, Action.straight, Action.straight)
    with pytest.raises(ValueError):
        extract_features(dead, SnakeId.A)


def test_wall_ahead_danger_dist_space() -> None:
    state = _place(
        a_body=(Cell(0, 5), Cell(1, 5), Cell(2, 5)),
        a_dir=Direction.W,
        b_body=(Cell(15, 15), Cell(16, 15), Cell(17, 15)),
        b_dir=Direction.W,
        food=Cell(10, 9),
    )
    vec = extract_features(state, SnakeId.A)
    assert vec[0] == 1
    assert vec[3] == pytest.approx(0.0)
    assert vec[6] == pytest.approx(0.0)


def test_food_diagonal_sets_two_bits() -> None:
    state = _place(
        a_body=(Cell(2, 2), Cell(1, 2), Cell(0, 2)),
        a_dir=Direction.E,
        b_body=(Cell(17, 17), Cell(18, 17), Cell(19, 17)),
        b_dir=Direction.W,
        food=Cell(4, 1),
    )
    vec = extract_features(state, SnakeId.A)
    assert vec[9] == 1
    assert vec[10] == 1
    assert vec[11] == 0
    assert vec[12] == 0


def test_equal_manhattan_opponent_not_closer() -> None:
    state = new_match(CoreConfig(), seed=0)
    vec = extract_features(state, SnakeId.A)
    assert vec[14] == 0


def test_head_risk_when_landing_is_opponent_next() -> None:
    state = _place(
        a_body=(Cell(5, 5), Cell(4, 5), Cell(3, 5)),
        a_dir=Direction.E,
        b_body=(Cell(6, 6), Cell(6, 7), Cell(6, 8)),
        b_dir=Direction.N,
        food=Cell(1, 1),
    )
    vec = extract_features(state, SnakeId.A)
    assert vec[16] == 1
