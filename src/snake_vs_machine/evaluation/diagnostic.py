"""Death-cause and critical-state helpers (D59 item 1)."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from snake_vs_machine.agents.base import ACTIONS, ActResult
from snake_vs_machine.agents.expert import ExpertAgent
from snake_vs_machine.agents.tree import TreeAgent
from snake_vs_machine.core.queries import is_fatal
from snake_vs_machine.core.state import Action, CoreConfig, EndReason, Side, SnakeId, State
from snake_vs_machine.services.match import MatchResult, play

DEATH_LABELS: tuple[str, ...] = (
    "wall",
    "obstacle",
    "self_body",
    "opponent_body",
    "head_to_head",
    "timeout",
)


def tree_death_cause(result: MatchResult, tree_id: SnakeId) -> str:
    cause = result.death_cause_a if tree_id is SnakeId.A else result.death_cause_b
    if result.end_reason is EndReason.timeout or cause is None:
        return "timeout"
    return cause.name


def is_critical(state: State, snake_id: SnakeId, expert: ExpertAgent) -> bool:
    expert_action = expert.act(state, snake_id)
    fatal_any = any(is_fatal(state, snake_id, action) for action in ACTIONS)
    return fatal_any or expert_action is not Action.straight


def count_deaths(causes: list[str]) -> Counter[str]:
    counts: Counter[str] = Counter({label: 0 for label in DEATH_LABELS})
    counts.update(causes)
    return counts


@dataclass(frozen=True, slots=True)
class ModelDiagnostic:
    name: str
    deaths: Counter[str]
    critical: int
    hits: int

    @property
    def accuracy(self) -> float:
        return self.hits / self.critical if self.critical else float("nan")


_PRODUCT: tuple[tuple[str, str, bool], ...] = (
    ("BC-3", "bc_depth3.joblib", False),
    ("BC-6", "bc_depth6.joblib", False),
    ("BC-8", "bc_depth8.joblib", True),
)


def run_product_diagnostic(n: int, models_dir: Path) -> list[ModelDiagnostic]:
    """N matches vs expert, alternating sides, product masks. Sequential."""
    rows: list[ModelDiagnostic] = []
    expert = ExpertAgent()
    config = CoreConfig()
    for name, filename, mask in _PRODUCT:
        tree = TreeAgent.from_joblib(models_dir / filename, safety_mask=mask)
        deaths: list[str] = []
        crit = 0
        hits = 0
        for index in range(n):
            tree_is_a = index % 2 == 0
            agent_a = tree if tree_is_a else expert
            agent_b = expert if tree_is_a else tree
            tree_side = SnakeId.A if tree_is_a else SnakeId.B

            def on_tick(
                before: State,
                result_a: ActResult,
                result_b: ActResult,
                after: State,
                side: SnakeId = tree_side,
            ) -> None:
                nonlocal crit, hits
                if not is_critical(before, side, expert):
                    return
                crit += 1
                played = result_a.action if side is SnakeId.A else result_b.action
                if played is expert.act(before, side):
                    hits += 1

            result = play(
                agent_a,
                agent_b,
                config,
                seed=index,
                sides={SnakeId.A: Side.NW, SnakeId.B: Side.SE},
                on_tick=on_tick,
            )
            deaths.append(tree_death_cause(result, tree_side))
        rows.append(ModelDiagnostic(name, count_deaths(deaths), crit, hits))
    return rows
