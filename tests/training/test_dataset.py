"""Dataset npz round-trip and the frozen 80/20 split (BR-SPL, D50 item 3)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from snake_vs_machine.core.features import FEATURE_SCHEMA_VERSION, feature_names
from snake_vs_machine.training.dataset import (
    LabelledRow,
    concat,
    from_rows,
    load_npz,
    save_npz,
    split_by_match,
)


def _row(match_id: int, y: int = 0, seed: int = 1) -> LabelledRow:
    return LabelledRow(
        features=tuple(float(i) for i in range(20)),
        y=y,
        match_id=match_id,
        seed=seed,
        tick=match_id,
        snake_index=0,
        pairing="expert_vs_expert",
        dagger_iter=0,
        expert_side=0,
    )


def test_round_trip_preserves_columns_and_metadata(tmp_path: Path) -> None:
    dataset = from_rows([_row(0), _row(1, y=2)])
    path = tmp_path / "rows.npz"
    save_npz(dataset, path)
    loaded = load_npz(path)
    assert loaded.X.shape == (2, 20)
    assert loaded.y.tolist() == [0, 2]
    assert loaded.match_id.tolist() == [0, 1]
    assert loaded.pairing.tolist() == ["expert_vs_expert", "expert_vs_expert"]
    assert loaded.feature_schema_version == FEATURE_SCHEMA_VERSION
    assert loaded.names == feature_names()
    assert loaded.numpy_version == np.__version__


def test_split_by_match_is_disjoint_80_20() -> None:
    rows = [_row(match_id, seed=match_id) for match_id in range(10) for _ in range(3)]
    train, test = split_by_match(from_rows(rows))
    train_ids = set(train.match_id.tolist())
    test_ids = set(test.match_id.tolist())
    assert train_ids.isdisjoint(test_ids)
    assert train_ids == {0, 1, 2, 3, 4, 5, 6, 7}
    assert test_ids == {8, 9}


def test_empty_rows_and_concat_raise() -> None:
    with pytest.raises(ValueError, match="no rows"):
        from_rows([])
    with pytest.raises(ValueError, match="empty list"):
        concat([])


def test_split_needs_two_match_ids() -> None:
    with pytest.raises(ValueError, match="at least two"):
        split_by_match(from_rows([_row(1)]))


def test_appending_to_train_does_not_change_test_ids() -> None:
    rows = [_row(match_id) for match_id in range(10)]
    train, test = split_by_match(from_rows(rows))
    frozen = set(test.match_id.tolist())
    extra = from_rows([_row(100, y=1)])
    grown = concat([train, extra])
    assert set(test.match_id.tolist()) == frozen
    assert 100 in set(grown.match_id.tolist())
    assert 100 not in frozen
