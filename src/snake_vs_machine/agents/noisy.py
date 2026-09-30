"""Feature-vector noise wrapper (D59 item 2). Lives in agents/ so registry stays layered."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from snake_vs_machine.agents.base import ActResult, ensure_playable, snake_index
from snake_vs_machine.agents.tree import TreeAgent
from snake_vs_machine.core.features import extract_features, feature_names
from snake_vs_machine.core.rng import noise_generator
from snake_vs_machine.core.state import Action, SnakeId, State

BINARY_FEATURES: frozenset[str] = frozenset(
    {
        "danger_ahead",
        "danger_left",
        "danger_right",
        "food_ahead",
        "food_left",
        "food_right",
        "food_behind",
        "head_risk_ahead",
        "head_risk_left",
        "head_risk_right",
        "opponent_closer_to_food",
    }
)
SKIP_NOISE = "length_diff"
DEFAULT_P_FLIP = 0.10
DEFAULT_SIGMA = 0.10


def apply_noise(
    vector: Sequence[float],
    names: Sequence[str],
    rng: np.random.Generator,
    p_flip: float = DEFAULT_P_FLIP,
    sigma: float = DEFAULT_SIGMA,
) -> list[float]:
    if len(vector) != len(names):
        raise ValueError("vector and names must have the same length")
    out = [float(value) for value in vector]
    for i, name in enumerate(names):
        if name == SKIP_NOISE:
            continue
        if name in BINARY_FEATURES:
            if float(rng.random()) < p_flip:
                out[i] = 1.0 - out[i]
        else:
            out[i] = min(1.0, max(0.0, out[i] + float(rng.normal(0.0, sigma))))
    return out


class NoisyTreeAgent:
    """extract_features → noise → TreeAgent.decide_from_vector; mask uses real State."""

    def __init__(self, tree: TreeAgent) -> None:
        self._tree = tree

    def decide(self, state: State, snake_id: SnakeId) -> ActResult:
        ensure_playable(state, snake_id)
        names = feature_names()
        raw = [float(value) for value in extract_features(state, snake_id)]
        rng = noise_generator(state.seed, state.tick, snake_index(snake_id))
        noisy = tuple(apply_noise(raw, names, rng))
        return self._tree.decide_from_vector(state, snake_id, noisy)

    def act(self, state: State, snake_id: SnakeId) -> Action:
        return self.decide(state, snake_id).action
