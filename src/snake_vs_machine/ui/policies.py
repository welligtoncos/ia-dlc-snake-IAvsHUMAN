"""Menu policy ids → labels and AgentSpecs (RF03)."""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path

from snake_vs_machine.agents.registry import AgentSpec


class PolicyId(StrEnum):
    random = "random"
    expert = "expert"
    easy = "easy"
    medium = "medium"
    hard = "hard"


LABELS: dict[PolicyId, str] = {
    PolicyId.random: "Aleatório",
    PolicyId.expert: "Especialista",
    PolicyId.easy: "Fácil",
    PolicyId.medium: "Médio",
    PolicyId.hard: "Difícil",
}

_TREE_FILES: dict[PolicyId, tuple[str, bool]] = {
    PolicyId.easy: ("bc_depth3.joblib", False),
    PolicyId.medium: ("bc_depth6.joblib", False),
    PolicyId.hard: ("bc_depth8.joblib", True),
}


def label(policy: PolicyId) -> str:
    return LABELS[policy]


def spec_for(policy: PolicyId, models_dir: Path) -> AgentSpec:
    if policy is PolicyId.random:
        return AgentSpec("random")
    if policy is PolicyId.expert:
        return AgentSpec("expert")
    filename, safety_mask = _TREE_FILES[policy]
    return AgentSpec(
        "tree",
        {"path": str(models_dir / filename), "safety_mask": safety_mask},
    )
