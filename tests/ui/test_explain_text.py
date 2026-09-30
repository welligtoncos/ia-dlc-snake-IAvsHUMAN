"""P-XPL-N and P-XPL-FMT (D59 item 3)."""

from __future__ import annotations

from snake_vs_machine.agents.tree import PathStep, TreeExplanation
from snake_vs_machine.core.state import Action
from snake_vs_machine.ui.explain_text import lines
from snake_vs_machine.ui.labels_pt import LABELS_PT


def _step(name: str, value: float, went_left: bool, threshold: float) -> PathStep:
    return PathStep(
        feature_name=name,
        threshold=threshold,
        feature_value=value,
        went_left=went_left,
    )


def _expl(*path: PathStep) -> TreeExplanation:
    return TreeExplanation(
        proposed=Action.straight,
        executed=Action.turn_left,
        vetoed=True,
        proba=(1.0, 0.0, 0.0),
        path=path,
    )


def test_veto_block_always_present() -> None:
    text = lines(_expl())
    assert text[:3] == ("proposta straight", "executada turn_left", "vetado: sim")


def test_at_most_three_conditions_are_the_tail() -> None:
    steps = tuple(
        _step("danger_ahead", float(i), True, 0.5) for i in range(5)
    )
    text = lines(_expl(*steps))
    conditions = text[3:]
    assert len(conditions) == 3
    assert "2.00" in conditions[0]
    assert "4.00" in conditions[2]


def test_went_left_uses_le_operator() -> None:
    text = lines(_expl(_step("dist_food", 0.25, True, 0.40)))
    label = LABELS_PT["dist_food"]
    assert text[-1] == f"{label} = 0.25 (≤ 0.40)"


def test_went_right_uses_gt_operator() -> None:
    text = lines(_expl(_step("dist_food", 0.80, False, 0.40)))
    label = LABELS_PT["dist_food"]
    assert text[-1] == f"{label} = 0.80 (> 0.40)"


def test_unknown_feature_raises() -> None:
    expl = _expl(_step("not_a_feature", 0.0, True, 0.0))
    try:
        lines(expl)
    except KeyError:
        return
    raise AssertionError("expected KeyError")
