"""Services: the match loop that drives core with a pair of agents (U3)."""

from snake_vs_machine.services.match import MatchResult, TickHook, play, tick

__all__ = [
    "MatchResult",
    "TickHook",
    "play",
    "tick",
]
