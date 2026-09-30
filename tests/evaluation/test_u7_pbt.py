"""U7 PBT: labels, path slice, noise clip/det, CI n<2 (D59)."""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from snake_vs_machine.agents.noisy import BINARY_FEATURES, SKIP_NOISE, apply_noise
from snake_vs_machine.agents.tree import PathStep, TreeExplanation
from snake_vs_machine.core.features import feature_names
from snake_vs_machine.core.rng import noise_generator
from snake_vs_machine.core.state import Action
from snake_vs_machine.evaluation.scoring import normal_ci, paired_difference_ci
from snake_vs_machine.ui.explain_text import lines
from snake_vs_machine.ui.labels_pt import LABELS_PT


@given(st.integers(min_value=0, max_value=8))
@settings(max_examples=20)
def test_p_xpl_n_at_most_three_conditions(extra: int) -> None:
    path = tuple(
        PathStep("danger_ahead", 0.5, float(i), True) for i in range(extra)
    )
    explanation = TreeExplanation(
        Action.straight, Action.straight, False, (1.0, 0.0, 0.0), path
    )
    assert len(lines(explanation)) == 3 + min(3, extra)


@given(st.booleans(), st.floats(0, 1, allow_nan=False, allow_infinity=False))
@settings(max_examples=20)
def test_p_xpl_fmt_operator(went_left: bool, value: float) -> None:
    step = PathStep("dist_food", 0.5, value, went_left)
    explanation = TreeExplanation(
        Action.straight, Action.straight, False, (1.0, 0.0, 0.0), (step,)
    )
    op = "≤" if went_left else ">"
    assert op in lines(explanation)[-1]


@given(st.integers(min_value=0, max_value=10_000), st.integers(0, 50), st.integers(0, 1))
@settings(max_examples=20)
def test_p_noi_det_and_clip(seed: int, tick: int, snake: int) -> None:
    names = feature_names()
    raw = [0.5] * len(names)
    raw[names.index(SKIP_NOISE)] = 0.31
    a = apply_noise(raw, names, noise_generator(seed, tick, snake))
    b = apply_noise(raw, names, noise_generator(seed, tick, snake))
    assert a == b
    assert a[names.index(SKIP_NOISE)] == 0.31
    for i, name in enumerate(names):
        if name != SKIP_NOISE and name not in BINARY_FEATURES:
            assert 0.0 <= a[i] <= 1.0


def test_p_lab_keys() -> None:
    assert set(LABELS_PT) == set(feature_names())


def test_p_ci_wide_n_one() -> None:
    assert normal_ci([0.5]) is None
    assert paired_difference_ci([1.0], [0.0]) is None
