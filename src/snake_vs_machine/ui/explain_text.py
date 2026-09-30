"""Pure RF05 strings from TreeExplanation (D59 item 3). No pygame."""

from __future__ import annotations

from snake_vs_machine.agents.tree import TreeExplanation
from snake_vs_machine.ui.labels_pt import LABELS_PT

_MAX_STEPS = 3


def _veto_lines(explanation: TreeExplanation) -> tuple[str, str, str]:
    vetado = "sim" if explanation.vetoed else "não"
    return (
        f"proposta {explanation.proposed.name}",
        f"executada {explanation.executed.name}",
        f"vetado: {vetado}",
    )


def _condition_line(feature_name: str, value: float, went_left: bool, threshold: float) -> str:
    label = LABELS_PT[feature_name]
    op = "≤" if went_left else ">"
    return f"{label} = {value:.2f} ({op} {threshold:.2f})"


def lines(explanation: TreeExplanation) -> tuple[str, ...]:
    """Veto block plus the last three path conditions (nearest the leaf)."""
    conditions = tuple(
        _condition_line(step.feature_name, step.feature_value, step.went_left, step.threshold)
        for step in explanation.path[-_MAX_STEPS:]
    )
    return _veto_lines(explanation) + conditions
