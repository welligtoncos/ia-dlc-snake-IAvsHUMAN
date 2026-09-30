"""TimedAgent records one sample per decide/act (D59 item 7)."""

from __future__ import annotations

from snake_vs_machine.agents.base import ActResult
from snake_vs_machine.core.setup import new_match
from snake_vs_machine.core.state import Action, CoreConfig, SnakeId
from snake_vs_machine.evaluation.timing import TimedAgent


class _Stub:
    def act(self, state, snake_id):
        return Action.straight


class _ExplainingStub:
    def act(self, state, snake_id):
        return self.decide(state, snake_id).action

    def decide(self, state, snake_id):
        return ActResult(Action.turn_left)


def test_times_act_on_plain_agent() -> None:
    wrapper = TimedAgent(_Stub())
    state = new_match(CoreConfig(), seed=0)
    assert wrapper.act(state, SnakeId.A) is Action.straight
    assert wrapper.samples == 1
    assert wrapper.mean_ms >= 0.0


def test_times_decide_once_when_act_delegates() -> None:
    wrapper = TimedAgent(_ExplainingStub())
    state = new_match(CoreConfig(), seed=0)
    result = wrapper.decide(state, SnakeId.A)
    assert result.action is Action.turn_left
    assert wrapper.samples == 1
    assert wrapper.act(state, SnakeId.A) is Action.turn_left
    assert wrapper.samples == 2
