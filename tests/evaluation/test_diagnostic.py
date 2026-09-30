"""Synthetic death-cause and critical helpers (D59 item 1)."""

from __future__ import annotations

from snake_vs_machine.agents.expert import ExpertAgent
from snake_vs_machine.core.setup import new_match
from snake_vs_machine.core.state import CoreConfig, DeathCause, EndReason, Outcome, Side, SnakeId
from snake_vs_machine.evaluation.diagnostic import is_critical, tree_death_cause
from snake_vs_machine.services.match import MatchResult


def _result(**kwargs: object) -> MatchResult:
    defaults: dict[str, object] = {
        "outcome": Outcome.draw,
        "end_reason": EndReason.death,
        "ticks": 4,
        "length_a": 3,
        "length_b": 3,
        "death_cause_a": DeathCause.wall,
        "death_cause_b": None,
        "seed": 0,
        "side_a": Side.NW,
        "side_b": Side.SE,
    }
    defaults.update(kwargs)
    return MatchResult(**defaults)  # type: ignore[arg-type]


def test_timeout_when_end_reason_is_timeout() -> None:
    result = _result(end_reason=EndReason.timeout, death_cause_a=None)
    assert tree_death_cause(result, SnakeId.A) == "timeout"


def test_named_cause_for_tree_side() -> None:
    result = _result(death_cause_b=DeathCause.head_to_head)
    assert tree_death_cause(result, SnakeId.B) == "head_to_head"


def test_is_critical_returns_bool_on_kickoff() -> None:
    state = new_match(CoreConfig(), seed=0)
    assert isinstance(is_critical(state, SnakeId.A, ExpertAgent()), bool)
