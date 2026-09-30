"""`.npz` labelled rows and the 80/20 match-id freeze (D21, D50 item 3, D52)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray

from snake_vs_machine.core.features import FEATURE_SCHEMA_VERSION, feature_names

_PAIRING_DTYPE = "U16"


@dataclass(frozen=True, slots=True)
class LabelledRow:
    features: tuple[float, ...]
    y: int
    match_id: int
    seed: int
    tick: int
    snake_index: int
    pairing: str
    dagger_iter: int
    expert_side: int


@dataclass(frozen=True, slots=True)
class Dataset:
    X: NDArray[np.float64]
    y: NDArray[np.int8]
    match_id: NDArray[np.int64]
    seed: NDArray[np.int64]
    tick: NDArray[np.int32]
    snake_index: NDArray[np.int8]
    pairing: NDArray[Any]
    dagger_iter: NDArray[np.int8]
    expert_side: NDArray[np.int8]
    feature_schema_version: int
    numpy_version: str
    names: tuple[str, ...]

    def __len__(self) -> int:
        return int(self.X.shape[0])


def from_rows(rows: list[LabelledRow], numpy_version: str | None = None) -> Dataset:
    if not rows:
        raise ValueError("cannot build a dataset from no rows")
    return Dataset(
        X=np.asarray([row.features for row in rows], dtype=np.float64),
        y=np.asarray([row.y for row in rows], dtype=np.int8),
        match_id=np.asarray([row.match_id for row in rows], dtype=np.int64),
        seed=np.asarray([row.seed for row in rows], dtype=np.int64),
        tick=np.asarray([row.tick for row in rows], dtype=np.int32),
        snake_index=np.asarray([row.snake_index for row in rows], dtype=np.int8),
        pairing=np.asarray([row.pairing for row in rows], dtype=_PAIRING_DTYPE),
        dagger_iter=np.asarray([row.dagger_iter for row in rows], dtype=np.int8),
        expert_side=np.asarray([row.expert_side for row in rows], dtype=np.int8),
        feature_schema_version=FEATURE_SCHEMA_VERSION,
        numpy_version=numpy_version if numpy_version is not None else np.__version__,
        names=feature_names(),
    )


def concat(parts: list[Dataset]) -> Dataset:
    if not parts:
        raise ValueError("cannot concatenate an empty list of datasets")
    head = parts[0]
    return Dataset(
        X=np.concatenate([part.X for part in parts], axis=0),
        y=np.concatenate([part.y for part in parts], axis=0),
        match_id=np.concatenate([part.match_id for part in parts], axis=0),
        seed=np.concatenate([part.seed for part in parts], axis=0),
        tick=np.concatenate([part.tick for part in parts], axis=0),
        snake_index=np.concatenate([part.snake_index for part in parts], axis=0),
        pairing=np.concatenate([part.pairing for part in parts], axis=0),
        dagger_iter=np.concatenate([part.dagger_iter for part in parts], axis=0),
        expert_side=np.concatenate([part.expert_side for part in parts], axis=0),
        feature_schema_version=head.feature_schema_version,
        numpy_version=head.numpy_version,
        names=head.names,
    )


def save_npz(dataset: Dataset, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        path,
        X=dataset.X,
        y=dataset.y,
        match_id=dataset.match_id,
        seed=dataset.seed,
        tick=dataset.tick,
        snake_index=dataset.snake_index,
        pairing=dataset.pairing,
        dagger_iter=dataset.dagger_iter,
        expert_side=dataset.expert_side,
        feature_schema_version=np.int32(dataset.feature_schema_version),
        numpy_version=np.asarray(dataset.numpy_version),
        feature_names=np.asarray(dataset.names, dtype="U32"),
    )


def load_npz(path: Path) -> Dataset:
    with np.load(path, allow_pickle=False) as payload:
        return Dataset(
            X=payload["X"],
            y=payload["y"],
            match_id=payload["match_id"],
            seed=payload["seed"],
            tick=payload["tick"],
            snake_index=payload["snake_index"],
            pairing=payload["pairing"],
            dagger_iter=payload["dagger_iter"],
            expert_side=payload["expert_side"],
            feature_schema_version=int(payload["feature_schema_version"]),
            numpy_version=str(payload["numpy_version"]),
            names=tuple(str(name) for name in payload["feature_names"].tolist()),
        )


def mask_by_ids(dataset: Dataset, ids: set[int]) -> Dataset:
    keep = np.isin(dataset.match_id, np.fromiter(ids, dtype=np.int64, count=len(ids)))
    return Dataset(
        X=dataset.X[keep],
        y=dataset.y[keep],
        match_id=dataset.match_id[keep],
        seed=dataset.seed[keep],
        tick=dataset.tick[keep],
        snake_index=dataset.snake_index[keep],
        pairing=dataset.pairing[keep],
        dagger_iter=dataset.dagger_iter[keep],
        expert_side=dataset.expert_side[keep],
        feature_schema_version=dataset.feature_schema_version,
        numpy_version=dataset.numpy_version,
        names=dataset.names,
    )


def split_by_match(dataset: Dataset) -> tuple[Dataset, Dataset]:
    """First 80% of sorted unique `match_id`s → train; the rest → test (BR-SPL-1)."""
    ids = np.unique(dataset.match_id)
    ids.sort()
    if ids.size < 2:
        raise ValueError("split_by_match needs at least two distinct match_id values")
    cut = int(0.8 * ids.size)
    if cut < 1:
        cut = 1
    if cut >= ids.size:
        cut = ids.size - 1
    train_ids = {int(value) for value in ids[:cut]}
    test_ids = {int(value) for value in ids[cut:]}
    return mask_by_ids(dataset, train_ids), mask_by_ids(dataset, test_ids)
