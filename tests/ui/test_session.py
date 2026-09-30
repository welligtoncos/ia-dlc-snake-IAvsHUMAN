"""Pure session machine (D58). No pygame."""

from __future__ import annotations

from snake_vs_machine.core.rng import ui_match_seed
from snake_vs_machine.core.state import Direction
from snake_vs_machine.ui.policies import PolicyId
from snake_vs_machine.ui.session import (
    ConfirmStart,
    LoadFailed,
    LoadPolicies,
    MatchOver,
    PoliciesReady,
    PushAbsolute,
    RequestTick,
    Screen,
    handle,
    new_session,
)


def _playing(seed: int = 7):
    state = new_session(seed)
    state, cmds = handle(state, ConfirmStart())
    assert any(isinstance(cmd, LoadPolicies) for cmd in cmds)
    state, _ = handle(state, PoliciesReady())
    assert state.screen is Screen.match
    assert state.match_index == 0
    assert state.match_seed == ui_match_seed(seed, 0)
    return state


def test_pause_ignores_movement() -> None:
    state = _playing()
    state, _ = handle(state, _key("p"))
    assert state.screen is Screen.paused
    state, cmds = handle(state, _key("w"))
    assert cmds == ()
    assert state.screen is Screen.paused


def test_n_while_paused_is_exactly_one_tick() -> None:
    state = _playing()
    state, _ = handle(state, _key("p"))
    state, cmds = handle(state, _key("n"))
    assert cmds == (RequestTick(),)


def test_r_starts_next_match_with_new_seed() -> None:
    state = _playing(7)
    state, cmds = handle(state, _key("r"))
    assert state.match_index == 1
    assert state.match_seed == ui_match_seed(7, 1)
    assert any(isinstance(cmd, LoadPolicies) for cmd in cmds)


def test_enter_on_end_is_rematch_with_incremented_index() -> None:
    state = _playing(7)
    state, _ = handle(state, MatchOver("a"))
    assert state.screen is Screen.end
    state, cmds = handle(state, _key("return"))
    assert state.match_index == 1
    assert state.match_seed == ui_match_seed(7, 1)
    assert any(isinstance(cmd, LoadPolicies) for cmd in cmds)


def test_esc_returns_to_menu() -> None:
    state = _playing()
    state, _ = handle(state, _key("escape"))
    assert state.screen is Screen.menu


def test_scoreboard_accumulates_then_zeros_on_menu() -> None:
    state = _playing()
    state, _ = handle(state, MatchOver("a"))
    assert state.score_a == 1
    assert state.score_b == 0
    state, _ = handle(state, _key("return"))
    state, _ = handle(state, PoliciesReady())
    state, _ = handle(state, MatchOver("a"))
    assert state.score_a == 2
    state, _ = handle(state, _key("escape"))
    assert state.screen is Screen.menu
    assert state.score_a == 0
    assert state.score_b == 0


def test_error4_from_match_any_key_returns_to_menu() -> None:
    state = _playing()
    state, _ = handle(state, LoadFailed("missing"))
    assert state.screen is Screen.error4
    state, _ = handle(state, _key("up"))
    assert state.screen is Screen.menu


def test_error4_from_menu_any_key_returns_to_menu() -> None:
    state = new_session(1)
    state, _ = handle(state, ConfirmStart())
    state, _ = handle(state, LoadFailed("schema"))
    assert state.screen is Screen.error4
    state, _ = handle(state, _key("p"))
    assert state.screen is Screen.menu


def test_human_match_push_absolute_while_playing() -> None:
    state = _playing()
    assert state.policy_a is PolicyId.easy or state.mode.value
    state, cmds = handle(state, _key("up"))
    assert cmds == (PushAbsolute(Direction.N),)


def _key(alias: str):
    from snake_vs_machine.ui.session import Key

    return Key(alias)
