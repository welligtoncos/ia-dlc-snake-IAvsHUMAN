"""Shared seed list and alignment for paired batteries (D60)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from snake_vs_machine.agents.registry import AgentSpec
from snake_vs_machine.core.rng import tournament_seed
from snake_vs_machine.core.state import CoreConfig, Side, SnakeId
from snake_vs_machine.evaluation.batch import MatchTask
from snake_vs_machine.evaluation.scoring import match_score
from snake_vs_machine.services.match import MatchResult

SIDES: dict[SnakeId, Side] = {SnakeId.A: Side.NW, SnakeId.B: Side.SE}


def seed_list(batch_seed: int, n: int) -> list[int]:
    return [tournament_seed(batch_seed, index) for index in range(n)]


def tree_is_a(index: int) -> bool:
    return index % 2 == 0


def tree_id(index: int) -> SnakeId:
    return SnakeId.A if tree_is_a(index) else SnakeId.B


def align_by_seeds(
    results: Sequence[MatchResult], seeds: Sequence[int]
) -> list[MatchResult]:
    by_seed: Mapping[int, MatchResult] = {result.seed: result for result in results}
    return [by_seed[seed] for seed in seeds]


def tree_scores(ordered: Sequence[MatchResult]) -> list[float]:
    return [
        match_score(result, tree_id(index)) for index, result in enumerate(ordered)
    ]


def battery_tasks(
    tree_spec: AgentSpec,
    n: int,
    batch_seed: int,
    config: CoreConfig | None = None,
) -> tuple[list[MatchTask], list[int]]:
    """Same seed list for every battery in a paired comparison (D60)."""
    cfg = config if config is not None else CoreConfig()
    seeds = seed_list(batch_seed, n)
    expert = AgentSpec("expert")
    tasks: list[MatchTask] = []
    for index, seed in enumerate(seeds):
        if tree_is_a(index):
            tasks.append(MatchTask(tree_spec, expert, cfg, seed, SIDES))
        else:
            tasks.append(MatchTask(expert, tree_spec, cfg, seed, SIDES))
    return tasks, seeds
