"""DAgger: three product trees vs the expert, one shared train set (D52 item 3)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import joblib

from snake_vs_machine.agents.base import ACTIONS, ActResult, Agent, snake_index
from snake_vs_machine.agents.expert import ExpertAgent
from snake_vs_machine.agents.registry import AgentSpec
from snake_vs_machine.agents.tree import TreeAgent
from snake_vs_machine.core.features import extract_features
from snake_vs_machine.core.rng import dagger_seed
from snake_vs_machine.core.state import CoreConfig, Side, SnakeId, State
from snake_vs_machine.evaluation.batch import MatchTask, run_imap, run_match
from snake_vs_machine.evaluation.scoring import summarise
from snake_vs_machine.services.match import play
from snake_vs_machine.training.dataset import Dataset, LabelledRow, concat, from_rows
from snake_vs_machine.training.fit import PRODUCT_DEPTHS, accuracy, fit_product_trees

N_ITERATIONS = 5


@dataclass(frozen=True, slots=True)
class DaggerTask:
    path: str
    config: CoreConfig
    seed: int
    match_id: int
    iteration: int
    student_is_a: bool


@dataclass(frozen=True, slots=True)
class IterationRecord:
    iteration: int
    n_new_rows: int
    accuracy_frozen: dict[int, float]
    score_vs_random: dict[int, float]
    draw_vs_random: dict[int, float]


def _side_code(state: State, snake_id: SnakeId) -> int:
    side = state.side_a if snake_id is SnakeId.A else state.side_b
    return 0 if side is Side.NW else 1


def dagger_match(task: DaggerTask) -> list[LabelledRow]:
    """One student-vs-expert match; label the student's pre-tick states."""
    student = TreeAgent.from_joblib(task.path, safety_mask=False)
    expert = ExpertAgent()
    if task.student_is_a:
        agent_a: Agent = student
        agent_b: Agent = expert
        keep = SnakeId.A
    else:
        agent_a = expert
        agent_b = student
        keep = SnakeId.B
    rows: list[LabelledRow] = []

    def on_tick(before: State, result_a: ActResult, result_b: ActResult, after: State) -> None:
        del result_a, result_b, after
        if before.end_reason is not None or not before.snake(keep).alive:
            return
        action = expert.act(before, keep)
        rows.append(
            LabelledRow(
                features=tuple(float(value) for value in extract_features(before, keep)),
                y=ACTIONS.index(action),
                match_id=task.match_id,
                seed=task.seed,
                tick=before.tick,
                snake_index=snake_index(keep),
                pairing="dagger",
                dagger_iter=task.iteration,
                expert_side=_side_code(before, keep),
            )
        )

    play(agent_a, agent_b, task.config, task.seed, on_tick=on_tick)
    return rows


def _vs_random_score(
    path: Path,
    config: CoreConfig,
    n: int,
    batch_seed: int,
    processes: int | None,
) -> tuple[float, float]:
    spec_tree = AgentSpec("tree", {"path": str(path), "safety_mask": False})
    spec_random = AgentSpec("random")
    tasks = [MatchTask(spec_tree, spec_random, config, seed=batch_seed + i) for i in range(n)]
    results = run_imap(run_match, tasks, processes=processes)
    summary = summarise(results)
    return summary.score_rate_a, summary.draw_rate


def _frozen_accuracy(paths: dict[int, Path], test: Dataset) -> dict[int, float]:
    scores: dict[int, float] = {}
    for depth, path in paths.items():
        clf = joblib.load(path)
        scores[depth] = accuracy(clf, test.X, test.y)
    return scores


def run_iteration(
    train: Dataset,
    test: Dataset,
    paths: dict[int, Path],
    iteration: int,
    batch_seed: int,
    target_rows: int,
    config: CoreConfig,
    vs_random_n: int,
    processes: int | None = 1,
    next_match_id: int = 1_000_000,
) -> tuple[Dataset, dict[int, Path], IterationRecord, int]:
    """Collect ~`target_rows` from all three students, append, refit, score."""
    if iteration < 1 or iteration > N_ITERATIONS:
        raise ValueError(f"DAgger iteration must be in 1..{N_ITERATIONS}")
    if target_rows < 1:
        raise ValueError("target_rows must be >= 1")
    collected: list[LabelledRow] = []
    match_index = 0
    match_id = next_match_id
    while len(collected) < target_rows:
        wave: list[DaggerTask] = []
        for depth in PRODUCT_DEPTHS:
            seed = dagger_seed(batch_seed, iteration, match_index)
            wave.append(
                DaggerTask(
                    path=str(paths[depth]),
                    config=config,
                    seed=seed,
                    match_id=match_id,
                    iteration=iteration,
                    student_is_a=match_index % 2 == 0,
                )
            )
            match_index += 1
            match_id += 1
        for chunk in run_imap(dagger_match, wave, processes=processes):
            collected.extend(chunk)
        print(
            f"dagger iter={iteration} collected={len(collected)}/{target_rows}",
            flush=True,
        )
    new_rows = collected
    combined = concat([train, from_rows(new_rows)])
    out_dir = paths[PRODUCT_DEPTHS[0]].parent
    new_paths = fit_product_trees(combined.X, combined.y, out_dir)
    acc = _frozen_accuracy(new_paths, test)
    scores: dict[int, float] = {}
    draws: dict[int, float] = {}
    if vs_random_n > 0:
        for depth, path in new_paths.items():
            score, draw = _vs_random_score(
                path,
                config,
                vs_random_n,
                batch_seed + iteration * 10_000 + depth,
                processes,
            )
            scores[depth] = score
            draws[depth] = draw
    record = IterationRecord(
        iteration=iteration,
        n_new_rows=len(new_rows),
        accuracy_frozen=acc,
        score_vs_random=scores,
        draw_vs_random=draws,
    )
    return combined, new_paths, record, match_id


def run_dagger(
    train: Dataset,
    test: Dataset,
    paths: dict[int, Path],
    batch_seed: int,
    target_rows: int,
    config: CoreConfig,
    vs_random_n: int,
    n_iterations: int = N_ITERATIONS,
    processes: int | None = 1,
) -> tuple[Dataset, dict[int, Path], list[IterationRecord]]:
    current_train = train
    current_paths = paths
    records: list[IterationRecord] = []
    next_match_id = int(train.match_id.max()) + 1_000_000
    for iteration in range(1, n_iterations + 1):
        current_train, current_paths, record, next_match_id = run_iteration(
            current_train,
            test,
            current_paths,
            iteration,
            batch_seed,
            target_rows,
            config,
            vs_random_n,
            processes=processes,
            next_match_id=next_match_id,
        )
        records.append(record)
        print(
            f"dagger iter={iteration} new_rows={record.n_new_rows} "
            f"acc={record.accuracy_frozen} vs_random={record.score_vs_random}",
            flush=True,
        )
    return current_train, current_paths, records
