"""DAgger keeps the frozen test ids and writes dagger rows (P-DAG-FROZEN)."""

from __future__ import annotations

from pathlib import Path

from snake_vs_machine.core.state import CoreConfig
from snake_vs_machine.training.collect import collect
from snake_vs_machine.training.dagger import run_dagger
from snake_vs_machine.training.dataset import split_by_match
from snake_vs_machine.training.fit import fit_product_trees


def test_dagger_does_not_change_test_match_ids(tmp_path: Path) -> None:
    config = CoreConfig(max_ticks=12)
    dataset = collect(16, batch_seed=5, config=config, processes=1)
    train, test = split_by_match(dataset)
    frozen = {int(v) for v in test.match_id.tolist()}
    paths = fit_product_trees(train.X, train.y, tmp_path)
    grown, new_paths, records = run_dagger(
        train,
        test,
        paths,
        batch_seed=5,
        target_rows=4,
        config=config,
            vs_random_n=2,
        n_iterations=2,
        processes=1,
    )
    assert {int(v) for v in test.match_id.tolist()} == frozen
    train_ids = {int(v) for v in train.match_id.tolist()}
    new_ids = {int(v) for v in grown.match_id.tolist()} - train_ids
    assert frozen.isdisjoint(new_ids)
    assert [rec.iteration for rec in records] == [1, 2]
    assert all(rec.n_new_rows >= 4 for rec in records)
    dagger_iters = {int(v) for v in grown.dagger_iter.tolist()}
    assert {1, 2} <= dagger_iters
    assert "dagger" in set(grown.pairing.tolist())
    assert set(new_paths) == {3, 6, 8}
    for rec in records:
        assert set(rec.accuracy_frozen) == {3, 6, 8}
