"""Collection labels are expert actions; sides alternate (P-COL-EXPERT, D52)."""

from __future__ import annotations

import pytest

from snake_vs_machine.agents.base import ACTIONS, ActResult, snake_index
from snake_vs_machine.agents.expert import ExpertAgent
from snake_vs_machine.agents.registry import build_agent
from snake_vs_machine.core.rng import collection_seed
from snake_vs_machine.core.state import CoreConfig, SnakeId, State
from snake_vs_machine.services.match import play
from snake_vs_machine.training.collect import CollectTask, _pair_tasks, collect, collect_match


def _tiny() -> CoreConfig:
    return CoreConfig(max_ticks=40)


def test_collect_rejects_non_positive_min_rows() -> None:
    with pytest.raises(ValueError, match="min_rows"):
        collect(0, batch_seed=1, config=_tiny(), processes=1)


def test_collect_reaches_min_rows_and_sets_metadata() -> None:
    dataset = collect(40, batch_seed=7, config=_tiny(), processes=1)
    assert len(dataset) >= 40
    assert set(dataset.pairing.tolist()) == {"expert_vs_expert", "expert_vs_random"}
    assert set(dataset.dagger_iter.tolist()) == {0}
    assert set(dataset.expert_side.tolist()) <= {0, 1}
    pairs = list(zip(dataset.match_id, dataset.pairing, strict=True))
    n_ee = len({int(m) for m, p in pairs if p == "expert_vs_expert"})
    n_evr = len({int(m) for m, p in pairs if p == "expert_vs_random"})
    assert n_ee == n_evr


def test_expert_vs_random_alternates_nw_se() -> None:
    _ee0, evr_nw = _pair_tasks(7, 0, _tiny())
    _ee1, evr_se = _pair_tasks(7, 2, _tiny())
    assert evr_nw.keep == (SnakeId.A,)
    assert evr_se.keep == (SnakeId.B,)
    assert evr_nw.seed == collection_seed(7, 1, 1)
    assert _ee0.seed == collection_seed(7, 0, 0)
    rows_nw = collect_match(evr_nw)
    rows_se = collect_match(evr_se)
    assert rows_nw
    assert rows_se
    assert set(row.expert_side for row in rows_nw) == {0}
    assert set(row.expert_side for row in rows_se) == {1}
    assert set(row.snake_index for row in rows_nw) == {0}
    assert set(row.snake_index for row in rows_se) == {1}


def test_every_label_matches_the_expert_on_that_state() -> None:
    config = CoreConfig(max_ticks=24)
    for start in (0, 2):
        ee, evr = _pair_tasks(3, start, config)
        for task in (ee, evr):
            _assert_task_labels_are_expert(task)


def _assert_task_labels_are_expert(task: CollectTask) -> None:
    rows = collect_match(task)
    expert = ExpertAgent()
    seen: list[tuple[int, int, int]] = []

    def on_tick(before: State, result_a: ActResult, result_b: ActResult, after: State) -> None:
        del result_a, result_b, after
        for sid in task.keep:
            if before.end_reason is not None or not before.snake(sid).alive:
                continue
            action = expert.act(before, sid)
            seen.append((before.tick, snake_index(sid), ACTIONS.index(action)))

    play(
        build_agent(task.spec_a),
        build_agent(task.spec_b),
        task.config,
        task.seed,
        on_tick=on_tick,
    )
    labelled = [(row.tick, row.snake_index, row.y) for row in rows]
    assert labelled == seen
