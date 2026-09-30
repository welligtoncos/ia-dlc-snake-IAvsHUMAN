"""P-NOI-CLIP and P-NOI-DET (D59 item 2)."""

from __future__ import annotations

from pathlib import Path

from snake_vs_machine.agents.noisy import BINARY_FEATURES, SKIP_NOISE, NoisyTreeAgent, apply_noise
from snake_vs_machine.agents.tree import TreeAgent
from snake_vs_machine.core.features import feature_names
from snake_vs_machine.core.rng import noise_generator
from snake_vs_machine.core.setup import new_match
from snake_vs_machine.core.state import CoreConfig, SnakeId

_TINY = Path(__file__).resolve().parents[2] / "models" / "fixtures" / "tiny_depth3.joblib"


def test_length_diff_unchanged_and_continuous_clipped() -> None:
    names = feature_names()
    raw = [0.0] * len(names)
    raw[names.index(SKIP_NOISE)] = 0.42
    rng = noise_generator(1, 0, 0)
    out = apply_noise(raw, names, rng, p_flip=1.0, sigma=10.0)
    assert out[names.index(SKIP_NOISE)] == 0.42
    for i, name in enumerate(names):
        if name == SKIP_NOISE:
            continue
        if name not in BINARY_FEATURES:
            assert 0.0 <= out[i] <= 1.0


def test_same_inputs_same_noisy_vector() -> None:
    names = feature_names()
    raw = [0.3] * len(names)
    a = apply_noise(raw, names, noise_generator(9, 2, 1))
    b = apply_noise(raw, names, noise_generator(9, 2, 1))
    assert a == b


def test_noisy_agent_decide_returns_action() -> None:
    tree = TreeAgent.from_joblib(_TINY, safety_mask=False)
    agent = NoisyTreeAgent(tree)
    state = new_match(CoreConfig(), seed=0)
    result = agent.decide(state, SnakeId.A)
    assert result.action is agent.act(state, SnakeId.A)
