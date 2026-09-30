"""1000 random matches via test helper (BR-A2). No RandomAgent class."""

from __future__ import annotations

from snake_vs_machine.core.engine import step
from snake_vs_machine.core.rng import helper_generator
from snake_vs_machine.core.setup import new_match
from snake_vs_machine.core.state import Action, CoreConfig

_ACTIONS = (Action.straight, Action.turn_left, Action.turn_right)


def play_random_match(seed: int, obstacle_count: int = 0) -> int:
    """Play until terminal. Actions from SeedSequence([seed, 2000003])."""
    rng = helper_generator(seed)
    state = new_match(CoreConfig(obstacle_count=obstacle_count), seed=seed)
    ticks = 0
    while state.end_reason is None:
        action_a = _ACTIONS[int(rng.integers(0, 3))]
        action_b = _ACTIONS[int(rng.integers(0, 3))]
        state = step(state, action_a, action_b)
        ticks += 1
    return ticks


def test_one_thousand_random_matches_no_exception() -> None:
    for seed in range(1000):
        play_random_match(seed, obstacle_count=(seed % 5) * 2)
