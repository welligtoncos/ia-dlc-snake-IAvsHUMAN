"""Paired seed list is shared across batteries (D60)."""

from __future__ import annotations

from snake_vs_machine.agents.registry import AgentSpec
from snake_vs_machine.core.rng import tournament_seed
from snake_vs_machine.evaluation.paired import battery_tasks, seed_list


def test_seed_list_has_no_pairing_code() -> None:
    seeds = seed_list(0, 3)
    assert seeds == [tournament_seed(0, 0), tournament_seed(0, 1), tournament_seed(0, 2)]


def test_two_batteries_share_seeds() -> None:
    a = AgentSpec("tree", {"path": "models/bc_depth8.joblib", "safety_mask": True})
    b = AgentSpec("tree", {"path": "models/bc_depth6.joblib", "safety_mask": False})
    tasks_a, seeds_a = battery_tasks(a, 4, 0)
    tasks_b, seeds_b = battery_tasks(b, 4, 0)
    assert seeds_a == seeds_b
    assert [task.seed for task in tasks_a] == [task.seed for task in tasks_b]
