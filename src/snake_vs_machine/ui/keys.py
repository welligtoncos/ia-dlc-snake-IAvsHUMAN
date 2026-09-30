"""Named key aliases. pygame `K_*` codes live in `pygame_keys` (D55 item 3)."""

from __future__ import annotations

from snake_vs_machine.core.state import Direction

MOVE_ALIASES: dict[str, Direction] = {
    "up": Direction.N,
    "w": Direction.N,
    "right": Direction.E,
    "d": Direction.E,
    "down": Direction.S,
    "s": Direction.S,
    "left": Direction.W,
    "a": Direction.W,
}

COMMAND_ALIASES: frozenset[str] = frozenset(
    {"escape", "p", "n", "r", "h", "return"}
)

KNOWN_ALIASES: frozenset[str] = frozenset(MOVE_ALIASES) | COMMAND_ALIASES


def direction_for(alias: str) -> Direction:
    try:
        return MOVE_ALIASES[alias]
    except KeyError:
        raise ValueError(f"unknown movement alias {alias!r}") from None


def is_known(alias: str) -> bool:
    return alias in KNOWN_ALIASES
