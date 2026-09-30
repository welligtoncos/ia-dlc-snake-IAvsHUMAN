"""Keyboard-driven agent: absolute commands, buffer of 2 (BR-HUM-1..11).

The only stateful agent. Key codes belong to U4: the UI translates a keypress
into a `Direction` before calling `push_absolute`.
"""

from __future__ import annotations

from collections import deque

from snake_vs_machine.agents.base import ensure_playable
from snake_vs_machine.core.state import Action, Direction, SnakeId, State, apply_action

_CAPACITY = 2


def _left_of(direction: Direction) -> Direction:
    return apply_action(direction, Action.turn_left)


def _right_of(direction: Direction) -> Direction:
    return apply_action(direction, Action.turn_right)


def _reverse(direction: Direction) -> Direction:
    return _left_of(_left_of(direction))


class HumanAgent:
    """Buffers absolute commands and converts one per tick into an action."""

    def __init__(self) -> None:
        self._buffer: deque[Direction] = deque()
        self._last_direction: Direction | None = None

    def pending(self) -> tuple[Direction, ...]:
        """The buffered commands, oldest first. Lets U4 preview the queue."""
        return tuple(self._buffer)

    def push_absolute(self, direction: Direction) -> None:
        """Enqueue an absolute command, filtering at push time (D44 item 4).

        The capacity check comes first: every buffered command was validated
        against its predecessor, so dropping the head to admit a newer key
        would leave a command validated against a direction that never
        happens — which is how a reverse gets in (D45 item 2).
        """
        if len(self._buffer) >= _CAPACITY:
            return
        effective = self._buffer[-1] if self._buffer else self._last_direction
        if effective is not None and direction in (effective, _reverse(effective)):
            return
        self._buffer.append(direction)

    def act(self, state: State, snake_id: SnakeId) -> Action:
        ensure_playable(state, snake_id)
        direction = state.snake(snake_id).direction
        self._last_direction = direction
        if not self._buffer:
            return Action.straight
        target = self._buffer.popleft()
        if target is _left_of(direction):
            return Action.turn_left
        if target is _right_of(direction):
            return Action.turn_right
        # Equal to the current direction, or a reverse that push filtering
        # should have rejected (BR-HUM-9).
        return Action.straight
