"""TreeAgent examples (BR-TREE, BR-MASK, BR-PROBA, BR-XPL, D50)."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from snake_vs_machine.agents.base import ActResult
from snake_vs_machine.agents.tree import (
    ModelLoadError,
    TreeAgent,
    TreeExplanation,
    _apply_mask,
)
from snake_vs_machine.core.features import extract_features
from snake_vs_machine.core.queries import is_fatal
from snake_vs_machine.core.rng import agent_generator
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

_REPO = Path(__file__).resolve().parents[2]
_FIXTURES = _REPO / "models" / "fixtures"
_TINY = _FIXTURES / "tiny_depth3.joblib"
_TWO = _FIXTURES / "two_class.joblib"
_STRAIGHT = _FIXTURES / "always_straight.joblib"


def _kickoff(seed: int = 0) -> State:
    return new_match(CoreConfig(), seed=seed)


def _wall_bound() -> State:
    """A at (19, 0) facing east: straight and left are out of the board."""
    state = _kickoff()
    snake_a = Snake(
        id=SnakeId.A,
        body=(Cell(19, 0), Cell(18, 0), Cell(17, 0)),
        direction=Direction.E,
    )
    return replace(state, snake_a=snake_a, obstacles=frozenset())


def _right_fatal() -> State:
    """A at (5, 19) facing east: turn_right leaves the board."""
    state = _kickoff()
    snake_a = Snake(
        id=SnakeId.A,
        body=(Cell(5, 19), Cell(4, 19), Cell(3, 19)),
        direction=Direction.E,
    )
    return replace(state, snake_a=snake_a)


def _straight_fatal() -> State:
    """A at (19, 5) facing east: only the two turns are on the board."""
    state = _kickoff()
    snake_a = Snake(
        id=SnakeId.A,
        body=(Cell(19, 5), Cell(18, 5), Cell(17, 5)),
        direction=Direction.E,
    )
    return replace(state, snake_a=snake_a)


def _boxed() -> State:
    state = _kickoff()
    snake_a = Snake(
        id=SnakeId.A,
        body=(Cell(19, 0), Cell(18, 0), Cell(17, 0)),
        direction=Direction.E,
    )
    return replace(state, snake_a=snake_a, obstacles=frozenset({Cell(19, 1)}))


def test_from_joblib_happy_path() -> None:
    agent = TreeAgent.from_joblib(_TINY)
    result = agent.decide(_kickoff(), SnakeId.A)
    assert isinstance(result, ActResult)
    assert isinstance(result.explanation, TreeExplanation)
    assert result.action in (Action.straight, Action.turn_left, Action.turn_right)


def test_missing_file_is_model_load_missing() -> None:
    with pytest.raises(ModelLoadError) as err:
        TreeAgent.from_joblib(_FIXTURES / "no_such_tree.joblib")
    assert err.value.code == "model_load"
    assert err.value.reason == "missing"


def test_sklearn_mismatch(tmp_path: Path) -> None:
    joblib_path = tmp_path / "bc.joblib"
    joblib_path.write_bytes(_TINY.read_bytes())
    meta = json.loads(_TINY.with_suffix(".json").read_text(encoding="utf-8"))
    meta["sklearn_version"] = "0.0.0"
    joblib_path.with_suffix(".json").write_text(json.dumps(meta), encoding="utf-8")
    with pytest.raises(ModelLoadError) as err:
        TreeAgent.from_joblib(joblib_path)
    assert err.value.reason == "sklearn"


def test_numpy_mismatch(tmp_path: Path) -> None:
    joblib_path = tmp_path / "bc.joblib"
    joblib_path.write_bytes(_TINY.read_bytes())
    meta = json.loads(_TINY.with_suffix(".json").read_text(encoding="utf-8"))
    meta["numpy_version"] = "0.0.0"
    joblib_path.with_suffix(".json").write_text(json.dumps(meta), encoding="utf-8")
    with pytest.raises(ModelLoadError) as err:
        TreeAgent.from_joblib(joblib_path)
    assert err.value.reason == "numpy"


def test_non_tree_joblib_is_schema(tmp_path: Path) -> None:
    import joblib

    joblib_path = tmp_path / "bc.joblib"
    joblib.dump({"not": "a tree"}, joblib_path)
    meta = json.loads(_TINY.with_suffix(".json").read_text(encoding="utf-8"))
    joblib_path.with_suffix(".json").write_text(json.dumps(meta), encoding="utf-8")
    with pytest.raises(ModelLoadError) as err:
        TreeAgent.from_joblib(joblib_path)
    assert err.value.reason == "schema"


def test_schema_mismatch(tmp_path: Path) -> None:
    joblib_path = tmp_path / "bc.joblib"
    joblib_path.write_bytes(_TINY.read_bytes())
    meta = json.loads(_TINY.with_suffix(".json").read_text(encoding="utf-8"))
    meta["feature_schema_version"] = 99
    joblib_path.with_suffix(".json").write_text(json.dumps(meta), encoding="utf-8")
    with pytest.raises(ModelLoadError) as err:
        TreeAgent.from_joblib(joblib_path)
    assert err.value.reason == "schema"


def test_rejects_terminal_and_dead() -> None:
    agent = TreeAgent.from_joblib(_TINY)
    with pytest.raises(ValueError, match="terminal"):
        agent.decide(replace(_kickoff(), end_reason=EndReason.timeout), SnakeId.A)
    dead = replace(_kickoff(), snake_a=replace(_kickoff().snake_a, alive=False))
    with pytest.raises(ValueError, match="dead snake A"):
        agent.act(dead, SnakeId.A)


def test_mask_off_keeps_proposed() -> None:
    agent = TreeAgent.from_joblib(_STRAIGHT, safety_mask=False)
    result = agent.decide(_wall_bound(), SnakeId.A)
    assert result.explanation is not None
    assert result.explanation.proposed is Action.straight
    assert result.explanation.executed is Action.straight
    assert result.explanation.vetoed is False


def test_worked_example_1_wall_bound_straight_becomes_right() -> None:
    state = _wall_bound()
    assert is_fatal(state, SnakeId.A, Action.straight)
    assert is_fatal(state, SnakeId.A, Action.turn_left)
    assert not is_fatal(state, SnakeId.A, Action.turn_right)
    agent = TreeAgent.from_joblib(_STRAIGHT, safety_mask=True)
    result = agent.decide(state, SnakeId.A)
    assert result.explanation is not None
    assert result.explanation.proposed is Action.straight
    assert result.explanation.executed is Action.turn_right
    assert result.explanation.vetoed is True


def test_worked_example_2_straight_wins_proba_tie() -> None:
    state = _right_fatal()
    assert is_fatal(state, SnakeId.A, Action.turn_right)
    assert not is_fatal(state, SnakeId.A, Action.straight)
    assert not is_fatal(state, SnakeId.A, Action.turn_left)
    executed, vetoed = _apply_mask(
        state, SnakeId.A, Action.turn_right, (0.4, 0.4, 0.2), True
    )
    assert executed is Action.straight
    assert vetoed is True


def test_worked_example_3_left_right_tie_follows_agent_stream() -> None:
    state = _straight_fatal()
    assert is_fatal(state, SnakeId.A, Action.straight)
    rng = agent_generator(state.seed, state.tick, 0)
    expected = (Action.turn_left, Action.turn_right)[int(rng.integers(2))]
    executed, vetoed = _apply_mask(
        state, SnakeId.A, Action.straight, (0.2, 0.4, 0.4), True
    )
    assert vetoed is True
    assert executed is expected
    again, _ = _apply_mask(state, SnakeId.A, Action.straight, (0.2, 0.4, 0.4), True)
    assert again is executed


def test_all_fatal_keeps_proposed() -> None:
    state = _boxed()
    assert all(is_fatal(state, SnakeId.A, action) for action in Action)
    agent = TreeAgent.from_joblib(_STRAIGHT, safety_mask=True)
    result = agent.decide(state, SnakeId.A)
    assert result.explanation is not None
    assert result.explanation.proposed is Action.straight
    assert result.explanation.executed is Action.straight
    assert result.explanation.vetoed is False


def test_missing_class_proba_slot_is_zero() -> None:
    agent = TreeAgent.from_joblib(_TWO)
    result = agent.decide(_kickoff(), SnakeId.A)
    assert result.explanation is not None
    assert result.explanation.proba[2] == 0.0
    assert result.action in (Action.straight, Action.turn_left)
    assert sum(result.explanation.proba) == pytest.approx(1.0)


def test_path_went_left_matches_threshold() -> None:
    agent = TreeAgent.from_joblib(_TINY)
    result = agent.decide(_kickoff(), SnakeId.A)
    assert result.explanation is not None
    assert result.explanation.path
    for step in result.explanation.path:
        assert step.went_left == (step.feature_value <= step.threshold)


def test_act_equals_decide_and_no_last_explanation() -> None:
    agent = TreeAgent.from_joblib(_TINY)
    state = _kickoff()
    assert agent.act(state, SnakeId.A) is agent.decide(state, SnakeId.A).action
    assert not hasattr(agent, "last_explanation")


def test_decide_from_vector_matches_decide() -> None:
    agent = TreeAgent.from_joblib(_TINY)
    state = _kickoff()
    vector = tuple(float(value) for value in extract_features(state, SnakeId.A))
    assert agent.decide_from_vector(state, SnakeId.A, vector) == agent.decide(state, SnakeId.A)


def test_decide_from_vector_rejects_wrong_length() -> None:
    agent = TreeAgent.from_joblib(_TINY)
    with pytest.raises(ValueError, match="feature vector length"):
        agent.decide_from_vector(_kickoff(), SnakeId.A, (0.0,))
