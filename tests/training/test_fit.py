"""Two fits on the same matrix are identical (P-FIT-DET, D50 item 4)."""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pytest
from sklearn.tree import export_text

from snake_vs_machine.training.dataset import LabelledRow, from_rows
from snake_vs_machine.training.fit import (
    RANDOM_STATE,
    fit_classifier,
    fit_product_trees,
    write_model,
)


def _toy_rows(n: int = 40) -> tuple[object, object]:
    rows = [
        LabelledRow(
            features=tuple(float((i + k) % 5) for k in range(20)),
            y=i % 3,
            match_id=i // 4,
            seed=i,
            tick=i,
            snake_index=i % 2,
            pairing="expert_vs_expert",
            dagger_iter=0,
            expert_side=0,
        )
        for i in range(n)
    ]
    dataset = from_rows(rows)
    return dataset.X, dataset.y


def test_accuracy_rejects_empty_matrix() -> None:
    from snake_vs_machine.training.fit import accuracy

    x, y = _toy_rows()
    clf = fit_classifier(x, y, 3)
    empty = np.empty((0, 20), dtype=np.float64)
    with pytest.raises(ValueError, match="empty"):
        accuracy(clf, empty, np.empty((0,), dtype=np.int8))


def test_two_fits_on_the_same_matrix_are_identical() -> None:
    x, y = _toy_rows()
    first = fit_classifier(x, y, max_depth=3)
    second = fit_classifier(x, y, max_depth=3)
    assert first.random_state == RANDOM_STATE
    assert export_text(first) == export_text(second)
    assert first.tree_.value.tolist() == second.tree_.value.tolist()


def test_fit_product_trees_writes_three_joblibs_and_json(tmp_path: Path) -> None:
    x, y = _toy_rows()
    paths = fit_product_trees(x, y, tmp_path)
    assert set(paths) == {3, 6, 8}
    for depth, path in paths.items():
        assert path.is_file()
        assert path.with_suffix(".json").is_file()
        loaded = joblib.load(path)
        assert loaded.get_depth() <= depth


def test_write_model_json_records_the_pin(tmp_path: Path) -> None:
    import json

    import numpy as np
    import sklearn

    x, y = _toy_rows()
    path = tmp_path / "bc_depth3.joblib"
    write_model(fit_classifier(x, y, 3), path, 3)
    meta = json.loads(path.with_suffix(".json").read_text(encoding="utf-8"))
    assert meta["sklearn_version"] == sklearn.__version__
    assert meta["numpy_version"] == np.__version__
    assert meta["random_state"] == RANDOM_STATE
    assert meta["max_depth"] == 3
