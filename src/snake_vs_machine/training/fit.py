"""Fit the three product depths and write `.joblib` + sibling JSON (D50, D51)."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import sklearn
from numpy.typing import NDArray
from sklearn.tree import DecisionTreeClassifier

from snake_vs_machine.core.features import FEATURE_SCHEMA_VERSION, feature_names

PRODUCT_DEPTHS: tuple[int, ...] = (3, 6, 8)
RANDOM_STATE = 0
MIN_SAMPLES_LEAF = 1
CRITERION = "gini"
CLASS_WEIGHT = "balanced"


def make_classifier(max_depth: int) -> DecisionTreeClassifier:
    return DecisionTreeClassifier(
        max_depth=max_depth,
        min_samples_leaf=MIN_SAMPLES_LEAF,
        criterion=CRITERION,
        class_weight=CLASS_WEIGHT,
        random_state=RANDOM_STATE,
    )


def fit_classifier(
    X: NDArray[np.float64], y: NDArray[np.int8], max_depth: int
) -> DecisionTreeClassifier:
    clf = make_classifier(max_depth)
    clf.fit(X, y)
    return clf


def write_model(clf: DecisionTreeClassifier, path: Path, max_depth: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(clf, path)
    payload = {
        "sklearn_version": sklearn.__version__,
        "numpy_version": np.__version__,
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "feature_names": list(feature_names()),
        "max_depth": max_depth,
        "min_samples_leaf": MIN_SAMPLES_LEAF,
        "criterion": CRITERION,
        "class_weight": CLASS_WEIGHT,
        "random_state": RANDOM_STATE,
    }
    path.with_suffix(".json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def fit_product_trees(
    X: NDArray[np.float64], y: NDArray[np.int8], out_dir: Path
) -> dict[int, Path]:
    """Fit depths 3/6/8 on `X, y` only — the caller must not pass the test split."""
    written: dict[int, Path] = {}
    for depth in PRODUCT_DEPTHS:
        path = out_dir / f"bc_depth{depth}.joblib"
        clf = fit_classifier(X, y, depth)
        write_model(clf, path, depth)
        written[depth] = path
    return written


def accuracy(
    clf: DecisionTreeClassifier, X: NDArray[np.float64], y: NDArray[np.int8]
) -> float:
    if X.shape[0] == 0:
        raise ValueError("cannot score an empty matrix")
    predicted = clf.predict(X)
    return float(np.mean(predicted == y))
