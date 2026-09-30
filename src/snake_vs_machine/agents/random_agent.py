"""Uniform draw over the non-fatal actions (BR-RND-1..4)."""

from __future__ import annotations

from snake_vs_machine.agents.base import ACTIONS, ensure_playable, snake_index
from snake_vs_machine.core.queries import is_fatal
from snake_vs_machine.core.rng import agent_generator
from snake_vs_machine.core.state import Action, SnakeId, State


class RandomAgent:
    """Stateless. The draw comes from the tick stream, not from the instance."""

    def act(self, state: State, snake_id: SnakeId) -> Action:
        ensure_playable(state, snake_id)
        candidates = [a for a in ACTIONS if not is_fatal(state, snake_id, a)]
        if not candidates:
            # Death is unavoidable; the agent still has to play (BR-RND-3).
            candidates = list(ACTIONS)
        rng = agent_generator(state.seed, state.tick, snake_index(snake_id))
        return candidates[int(rng.integers(len(candidates)))]
