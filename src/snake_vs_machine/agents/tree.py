"""Decision-tree agent: load a fitted sklearn tree and optionally mask fatalities (U5)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import sklearn
from numpy.typing import NDArray
from sklearn.tree import DecisionTreeClassifier

from snake_vs_machine.agents.base import (
    ACTIONS,
    ActResult,
    ensure_playable,
    snake_index,
)
from snake_vs_machine.core.features import FEATURE_SCHEMA_VERSION, extract_features, feature_names
from snake_vs_machine.core.queries import is_fatal
from snake_vs_machine.core.rng import agent_generator
from snake_vs_machine.core.state import Action, SnakeId, State

_LEAF_FEATURE = -2


class ModelLoadError(Exception):
    """Library-side load failure. U4 owns the Portuguese erro 4 text."""

    def __init__(self, reason: str) -> None:
        self.code = "model_load"
        self.reason = reason
        super().__init__(f"model_load:{reason}")


@dataclass(frozen=True, slots=True)
class ModelMeta:
    sklearn_version: str
    numpy_version: str
    feature_schema_version: int
    feature_names: tuple[str, ...]
    max_depth: int
    min_samples_leaf: int
    criterion: str
    class_weight: str
    random_state: int


@dataclass(frozen=True, slots=True)
class PathStep:
    feature_name: str
    threshold: float
    feature_value: float
    went_left: bool


@dataclass(frozen=True, slots=True)
class TreeExplanation:
    proposed: Action
    executed: Action
    vetoed: bool
    proba: tuple[float, float, float]
    path: tuple[PathStep, ...]


def _map_proba(classes: NDArray[Any], raw: NDArray[Any]) -> tuple[float, float, float]:
    """Map `predict_proba` onto `_ACTIONS` order. A missing class is 0 (D50 item 7)."""
    out = [0.0, 0.0, 0.0]
    for probability, cls in zip(raw.tolist(), classes.tolist(), strict=True):
        idx = int(cls)
        if 0 <= idx < 3:
            out[idx] = float(probability)
    return (out[0], out[1], out[2])


def _map_label(cls: int | np.integer[Any]) -> Action:
    return ACTIONS[int(cls)]


def _apply_mask(
    state: State,
    snake_id: SnakeId,
    proposed: Action,
    proba: tuple[float, float, float],
    safety_mask: bool,
) -> tuple[Action, bool]:
    if not safety_mask or not is_fatal(state, snake_id, proposed):
        return proposed, False
    safe = [action for action in ACTIONS if not is_fatal(state, snake_id, action)]
    if not safe:
        return proposed, False
    best = max(proba[ACTIONS.index(action)] for action in safe)
    tied = [action for action in ACTIONS if action in safe and proba[ACTIONS.index(action)] == best]
    if Action.straight in tied:
        return Action.straight, True
    rng = agent_generator(state.seed, state.tick, snake_index(snake_id))
    return tied[int(rng.integers(len(tied)))], True


def _path_steps(tree: DecisionTreeClassifier, vector: tuple[float, ...]) -> tuple[PathStep, ...]:
    names = feature_names()
    row = np.asarray([vector], dtype=np.float64)
    indicator = tree.decision_path(row)
    node_ids = indicator.indices[indicator.indptr[0] : indicator.indptr[1]]
    structure = tree.tree_
    steps: list[PathStep] = []
    for node in node_ids:
        feat = int(structure.feature[node])
        if feat == _LEAF_FEATURE:
            continue
        value = float(vector[feat])
        threshold = float(structure.threshold[node])
        steps.append(
            PathStep(
                feature_name=names[feat],
                threshold=threshold,
                feature_value=value,
                went_left=value <= threshold,
            )
        )
    return tuple(steps)


def _read_meta(path: Path) -> ModelMeta:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return ModelMeta(
        sklearn_version=str(payload["sklearn_version"]),
        numpy_version=str(payload["numpy_version"]),
        feature_schema_version=int(payload["feature_schema_version"]),
        feature_names=tuple(payload["feature_names"]),
        max_depth=int(payload["max_depth"]),
        min_samples_leaf=int(payload["min_samples_leaf"]),
        criterion=str(payload["criterion"]),
        class_weight=str(payload["class_weight"]),
        random_state=int(payload["random_state"]),
    )


class TreeAgent:
    """A fitted tree plus an optional `is_fatal` mask. Stateless about explanations."""

    def __init__(
        self,
        tree: DecisionTreeClassifier,
        meta: ModelMeta,
        safety_mask: bool = False,
    ) -> None:
        self._tree = tree
        self._meta = meta
        self._safety_mask = safety_mask

    @classmethod
    def from_joblib(cls, path: str | Path, safety_mask: bool = False) -> TreeAgent:
        joblib_path = Path(path)
        json_path = joblib_path.with_suffix(".json")
        if not joblib_path.is_file() or not json_path.is_file():
            raise ModelLoadError("missing")
        meta = _read_meta(json_path)
        if meta.sklearn_version != sklearn.__version__:
            raise ModelLoadError("sklearn")
        if meta.numpy_version != np.__version__:
            raise ModelLoadError("numpy")
        if (
            meta.feature_schema_version != FEATURE_SCHEMA_VERSION
            or meta.feature_names != feature_names()
        ):
            raise ModelLoadError("schema")
        tree = joblib.load(joblib_path)
        if not isinstance(tree, DecisionTreeClassifier):
            raise ModelLoadError("schema")
        return cls(tree, meta, safety_mask)

    def decide_from_vector(
        self,
        state: State,
        snake_id: SnakeId,
        vector: tuple[float, ...],
    ) -> ActResult:
        """Predict and mask from a caller-supplied feature vector (D59 noise)."""
        ensure_playable(state, snake_id)
        names = feature_names()
        if len(vector) != len(names):
            raise ValueError(f"feature vector length {len(vector)} != {len(names)}")
        row = np.asarray([vector], dtype=np.float64)
        proba = _map_proba(self._tree.classes_, self._tree.predict_proba(row)[0])
        proposed = _map_label(self._tree.predict(row)[0])
        executed, vetoed = _apply_mask(state, snake_id, proposed, proba, self._safety_mask)
        explanation = TreeExplanation(
            proposed=proposed,
            executed=executed,
            vetoed=vetoed,
            proba=proba,
            path=_path_steps(self._tree, vector),
        )
        return ActResult(executed, explanation)

    def decide(self, state: State, snake_id: SnakeId) -> ActResult:
        ensure_playable(state, snake_id)
        raw_features = extract_features(state, snake_id)
        vector = tuple(float(value) for value in raw_features)
        return self.decide_from_vector(state, snake_id, vector)

    def act(self, state: State, snake_id: SnakeId) -> Action:
        return self.decide(state, snake_id).action
