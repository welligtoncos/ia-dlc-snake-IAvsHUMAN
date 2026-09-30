"""Property-based tests for TreeAgent (P-TREE-*, PBT-02/03/07/08/09)."""

from __future__ import annotations

from pathlib import Path

from hypothesis import given
from hypothesis import strategies as st

from snake_vs_machine.agents.base import ACTIONS
from snake_vs_machine.agents.tree import TreeAgent, TreeExplanation
from snake_vs_machine.core.features import extract_features, feature_names
from snake_vs_machine.core.queries import is_fatal
from snake_vs_machine.core.state import Action, SnakeId, copy
from tests.core.test_features_pbt import playing_state

_TINY = Path(__file__).resolve().parents[2] / "models" / "fixtures" / "tiny_depth3.joblib"
_OFF = TreeAgent.from_joblib(_TINY, safety_mask=False)
_ON = TreeAgent.from_joblib(_TINY, safety_mask=True)


@given(playing_state(), st.sampled_from(list(SnakeId)))
def test_p_tree_action_pure_frozen(state: object, snake_id: SnakeId) -> None:
    if state.end_reason is not None or not state.snake(snake_id).alive:
        return
    before = copy(state)
    for agent in (_OFF, _ON):
        result = agent.decide(state, snake_id)
        assert result.action in ACTIONS
        assert agent.act(state, snake_id) is result.action
        assert agent.decide(state, snake_id) == result
        assert state == before
        assert isinstance(result.explanation, TreeExplanation)


@given(playing_state(), st.sampled_from(list(SnakeId)))
def test_p_tree_mask_invariants(state: object, snake_id: SnakeId) -> None:
    if state.end_reason is not None or not state.snake(snake_id).alive:
        return
    result = _ON.decide(state, snake_id)
    assert result.explanation is not None
    safe = [action for action in ACTIONS if not is_fatal(state, snake_id, action)]
    if safe:
        assert not is_fatal(state, snake_id, result.explanation.executed)
    else:
        assert result.explanation.executed is result.explanation.proposed
        assert result.explanation.vetoed is False
    vetoed = result.explanation.executed is not result.explanation.proposed
    assert result.explanation.vetoed is vetoed


@given(playing_state(), st.sampled_from(list(SnakeId)))
def test_p_tree_proba_and_path(state: object, snake_id: SnakeId) -> None:
    if state.end_reason is not None or not state.snake(snake_id).alive:
        return
    result = _OFF.decide(state, snake_id)
    assert result.explanation is not None
    assert len(result.explanation.proba) == 3
    assert abs(sum(result.explanation.proba) - 1.0) < 1e-9
    vector = tuple(float(v) for v in extract_features(state, snake_id))
    names = feature_names()
    for step in result.explanation.path:
        assert step.feature_name in names
        assert step.went_left == (step.feature_value <= step.threshold)
        idx = names.index(step.feature_name)
        assert step.feature_value == vector[idx]
    assert result.action in (Action.straight, Action.turn_left, Action.turn_right)
