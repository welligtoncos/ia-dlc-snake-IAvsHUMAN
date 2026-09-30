"""Build the tiny committed fixture trees used by U5 tests."""

from __future__ import annotations

from pathlib import Path

from snake_vs_machine.agents.base import ACTIONS
from snake_vs_machine.agents.expert import ExpertAgent
from snake_vs_machine.core.engine import step
from snake_vs_machine.core.features import extract_features
from snake_vs_machine.core.setup import new_match
from snake_vs_machine.core.state import Action, CoreConfig, SnakeId
from snake_vs_machine.training.fit import fit_classifier, write_model

_ROOT = Path(__file__).resolve().parents[1]
_OUT = _ROOT / "models" / "fixtures"


def _labelled_rows(n_matches: int) -> tuple[list[list[float]], list[int]]:
    expert = ExpertAgent()
    config = CoreConfig(max_ticks=40)
    xs: list[list[float]] = []
    ys: list[int] = []
    for seed in range(n_matches):
        state = new_match(config, seed)
        ticks = 0
        while state.end_reason is None and ticks < 8:
            for snake_id in (SnakeId.A, SnakeId.B):
                if not state.snake(snake_id).alive:
                    continue
                features = [float(v) for v in extract_features(state, snake_id)]
                label = ACTIONS.index(expert.act(state, snake_id))
                xs.append(features)
                ys.append(label)
            state = step(state, Action.straight, Action.straight)
            ticks += 1
    for label in (0, 1, 2):
        xs.append([float(label + 3)] * 20)
        ys.append(label)
    return xs, ys


def main() -> None:
    _OUT.mkdir(parents=True, exist_ok=True)
    xs, ys = _labelled_rows(60)
    two_x = [row for row, label in zip(xs, ys, strict=True) if label != 2]
    two_y = [label for label in ys if label != 2]
    if len(set(two_y)) < 2:
        raise SystemExit("two-class fixture needs both straight and turn_left")
    if len(set(ys)) < 3:
        raise SystemExit("tiny_depth3 fixture needs all three actions")

    import numpy as np

    x_all = np.asarray(xs, dtype=np.float64)
    y_all = np.asarray(ys, dtype=np.int8)
    write_model(fit_classifier(x_all, y_all, max_depth=3), _OUT / "tiny_depth3.joblib", 3)

    x_two = np.asarray(two_x, dtype=np.float64)
    y_two = np.asarray(two_y, dtype=np.int8)
    write_model(fit_classifier(x_two, y_two, max_depth=3), _OUT / "two_class.joblib", 3)

    x_straight = x_all
    y_straight = np.zeros(len(ys), dtype=np.int8)
    straight = fit_classifier(x_straight, y_straight, max_depth=1)
    write_model(straight, _OUT / "always_straight.joblib", 1)
    print(f"wrote fixtures to {_OUT} n={len(ys)} classes={sorted(set(ys))}")


if __name__ == "__main__":
    main()
