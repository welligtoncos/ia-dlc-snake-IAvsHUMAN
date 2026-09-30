"""Initial BC collection: expert vs expert and expert vs random (D52)."""

from __future__ import annotations

from dataclasses import dataclass

from snake_vs_machine.agents.base import ACTIONS, ActResult, snake_index
from snake_vs_machine.agents.expert import ExpertAgent
from snake_vs_machine.agents.registry import AgentSpec, build_agent
from snake_vs_machine.core.features import extract_features
from snake_vs_machine.core.rng import collection_seed
from snake_vs_machine.core.state import CoreConfig, Side, SnakeId, State
from snake_vs_machine.evaluation.batch import run_imap
from snake_vs_machine.services.match import play
from snake_vs_machine.training.dataset import Dataset, LabelledRow, concat, from_rows

_PAIRING_CODE = {"expert_vs_expert": 0, "expert_vs_random": 1}
_DEFAULT_SIDES = {SnakeId.A: Side.NW, SnakeId.B: Side.SE}


@dataclass(frozen=True, slots=True)
class CollectTask:
    spec_a: AgentSpec
    spec_b: AgentSpec
    config: CoreConfig
    seed: int
    match_id: int
    pairing: str
    keep: tuple[SnakeId, ...]


def _side_code(state: State, snake_id: SnakeId) -> int:
    side = state.side_a if snake_id is SnakeId.A else state.side_b
    return 0 if side is Side.NW else 1


def _row(state: State, snake_id: SnakeId, action_index: int, task: CollectTask) -> LabelledRow:
    features = tuple(float(value) for value in extract_features(state, snake_id))
    return LabelledRow(
        features=features,
        y=action_index,
        match_id=task.match_id,
        seed=task.seed,
        tick=state.tick,
        snake_index=snake_index(snake_id),
        pairing=task.pairing,
        dagger_iter=0,
        expert_side=_side_code(state, snake_id),
    )


def collect_match(task: CollectTask) -> list[LabelledRow]:
    """Module-level worker: one match, labelled expert rows (Windows `spawn`)."""
    expert = ExpertAgent()
    rows: list[LabelledRow] = []

    def on_tick(before: State, result_a: ActResult, result_b: ActResult, after: State) -> None:
        del result_a, result_b, after
        for sid in task.keep:
            if before.end_reason is not None or not before.snake(sid).alive:
                continue
            action = expert.act(before, sid)
            rows.append(_row(before, sid, ACTIONS.index(action), task))

    play(
        build_agent(task.spec_a),
        build_agent(task.spec_b),
        task.config,
        task.seed,
        sides=_DEFAULT_SIDES,
        on_tick=on_tick,
    )
    return rows


def _pair_tasks(
    batch_seed: int, match_id: int, config: CoreConfig
) -> tuple[CollectTask, CollectTask]:
    """One expert-vs-expert and one expert-vs-random with alternating expert side."""
    expert = AgentSpec("expert")
    random = AgentSpec("random")
    ee_seed = collection_seed(batch_seed, _PAIRING_CODE["expert_vs_expert"], match_id)
    evr_seed = collection_seed(batch_seed, _PAIRING_CODE["expert_vs_random"], match_id + 1)
    ee = CollectTask(
        spec_a=expert,
        spec_b=expert,
        config=config,
        seed=ee_seed,
        match_id=match_id,
        pairing="expert_vs_expert",
        keep=(SnakeId.A, SnakeId.B),
    )
    if (match_id // 2) % 2 == 0:
        evr = CollectTask(
            spec_a=expert,
            spec_b=random,
            config=config,
            seed=evr_seed,
            match_id=match_id + 1,
            pairing="expert_vs_random",
            keep=(SnakeId.A,),
        )
    else:
        evr = CollectTask(
            spec_a=random,
            spec_b=expert,
            config=config,
            seed=evr_seed,
            match_id=match_id + 1,
            pairing="expert_vs_random",
            keep=(SnakeId.B,),
        )
    return ee, evr


def collect(
    min_rows: int,
    batch_seed: int,
    config: CoreConfig,
    processes: int | None = 1,
) -> Dataset:
    """Collect until `min_rows`, always adding ee and evr in equal match counts."""
    if min_rows < 1:
        raise ValueError("min_rows must be >= 1")
    parts: list[Dataset] = []
    total = 0
    match_id = 0
    while total < min_rows:
        remaining = min_rows - total
        optimistic_rows_per_pair = max(1, config.max_ticks)
        per_pair = optimistic_rows_per_pair
        n_pairs = max(1, min(16, (remaining + per_pair - 1) // per_pair))
        wave: list[CollectTask] = []
        for _ in range(n_pairs):
            ee, evr = _pair_tasks(batch_seed, match_id, config)
            wave.extend((ee, evr))
            match_id += 2
        chunks = run_imap(collect_match, wave, processes=processes)
        rows = [row for chunk in chunks for row in chunk]
        if not rows:
            raise RuntimeError("collection produced no labelled rows")
        part = from_rows(rows)
        parts.append(part)
        total += len(part)
    return concat(parts)
