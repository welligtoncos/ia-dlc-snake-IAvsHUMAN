"""Agent contracts (D44 item 1, D45 item 1).

Structural protocols, not base classes: a test double is a plain object with
the right method, and the U5 `TreeAgent` satisfies `ExplainingAgent` without
importing anything from this module at runtime.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from snake_vs_machine.core.state import Action, SnakeId, State

ACTIONS: tuple[Action, ...] = (Action.straight, Action.turn_left, Action.turn_right)

_SNAKE_INDEX: dict[SnakeId, int] = {SnakeId.A: 0, SnakeId.B: 1}


def snake_index(snake_id: SnakeId) -> int:
    """0 for A, 1 for B — written out, never `SnakeId.A.value` (D44 item 3)."""
    return _SNAKE_INDEX[snake_id]


@runtime_checkable
class ExplanationPayload(Protocol):
    """Marker for U5's explanation data; opaque to U3.

    Empty on purpose. U3 has to name the type that flows through `on_tick`
    without inventing U5's fields (decision path, proposed action, executed
    action, veto flag — D30).
    """


@dataclass(frozen=True, slots=True)
class ActResult:
    """The action actually executed, plus its explanation when there is one."""

    action: Action
    explanation: ExplanationPayload | None = None


class Agent(Protocol):
    """Every agent in the project, including U5's `TreeAgent`."""

    def act(self, state: State, snake_id: SnakeId) -> Action:
        """The action this agent plays for `snake_id` on `state`.

        The side is a parameter, so one instance can play either snake and
        tournament side alternation needs no rebuild (Q1=B).
        """
        ...


@runtime_checkable
class ExplainingAgent(Protocol):
    """Optional second contract, implemented only by U5's `TreeAgent`.

    `runtime_checkable` because `services.match` routes on `isinstance`. That
    check only looks at method names, which is enough here: `decide` is a name
    no other agent defines.
    """

    def act(self, state: State, snake_id: SnakeId) -> Action: ...

    def decide(self, state: State, snake_id: SnakeId) -> ActResult: ...


def ensure_playable(state: State, snake_id: SnakeId) -> None:
    """Guard shared by the agents: no acting on a finished match (BR-AGT-5)."""
    if state.end_reason is not None:
        raise ValueError("cannot act on a terminal state")
    if not state.snake(snake_id).alive:
        raise ValueError(f"cannot act for dead snake {snake_id.name}")
