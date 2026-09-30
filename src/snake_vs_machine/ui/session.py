"""Pure UI session machine. No pygame (D58)."""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum

from snake_vs_machine.core.rng import ui_match_seed
from snake_vs_machine.core.state import Direction
from snake_vs_machine.ui.clock import consume
from snake_vs_machine.ui.keys import MOVE_ALIASES, direction_for
from snake_vs_machine.ui.policies import PolicyId


class Screen(StrEnum):
    menu = "menu"
    match = "match"
    paused = "paused"
    end = "end"
    error4 = "error4"


class MatchMode(StrEnum):
    human_vs_ai = "human_vs_ai"
    spectator = "spectator"


@dataclass(frozen=True, slots=True)
class SessionState:
    screen: Screen
    match_index: int
    mode: MatchMode
    policy_a: PolicyId
    policy_b: PolicyId
    score_a: int
    score_b: int
    session_seed: int
    match_seed: int
    acc: float
    panel_visible: bool
    error_reason: str | None
    tick_rate: int


@dataclass(frozen=True, slots=True)
class Key:
    alias: str


@dataclass(frozen=True, slots=True)
class TickDt:
    dt: float


@dataclass(frozen=True, slots=True)
class ConfirmStart:
    pass


@dataclass(frozen=True, slots=True)
class PoliciesReady:
    pass


@dataclass(frozen=True, slots=True)
class LoadFailed:
    reason: str


@dataclass(frozen=True, slots=True)
class MatchOver:
    winner: str  # "a" | "b" | "draw"


@dataclass(frozen=True, slots=True)
class SetPolicyB:
    policy: PolicyId


@dataclass(frozen=True, slots=True)
class SetMode:
    mode: MatchMode


@dataclass(frozen=True, slots=True)
class PushAbsolute:
    direction: Direction


@dataclass(frozen=True, slots=True)
class RequestTick:
    pass


@dataclass(frozen=True, slots=True)
class LoadPolicies:
    pass


@dataclass(frozen=True, slots=True)
class QuitApp:
    pass


Event = (
    Key
    | TickDt
    | ConfirmStart
    | PoliciesReady
    | LoadFailed
    | MatchOver
    | SetPolicyB
    | SetMode
)
Command = PushAbsolute | RequestTick | LoadPolicies | QuitApp


def new_session(session_seed: int, tick_rate: int = 10) -> SessionState:
    return SessionState(
        screen=Screen.menu,
        match_index=0,
        mode=MatchMode.human_vs_ai,
        policy_a=PolicyId.easy,
        policy_b=PolicyId.medium,
        score_a=0,
        score_b=0,
        session_seed=session_seed,
        match_seed=0,
        acc=0.0,
        panel_visible=True,
        error_reason=None,
        tick_rate=tick_rate,
    )


def _to_menu(state: SessionState) -> SessionState:
    return replace(
        state,
        screen=Screen.menu,
        match_index=0,
        score_a=0,
        score_b=0,
        acc=0.0,
        error_reason=None,
        match_seed=0,
    )


def _begin_match(state: SessionState, match_index: int) -> tuple[SessionState, tuple[Command, ...]]:
    seed = ui_match_seed(state.session_seed, match_index)
    nxt = replace(
        state,
        match_index=match_index,
        match_seed=seed,
        acc=0.0,
        error_reason=None,
        screen=Screen.menu,
    )
    return nxt, (LoadPolicies(),)


def _after_load(state: SessionState) -> SessionState:
    return replace(state, screen=Screen.match, error_reason=None)


def handle(state: SessionState, event: Event) -> tuple[SessionState, tuple[Command, ...]]:
    if isinstance(event, LoadFailed):
        return replace(state, screen=Screen.error4, error_reason=event.reason), ()

    if state.screen is Screen.error4:
        if isinstance(event, Key):
            return _to_menu(state), ()
        return state, ()

    if isinstance(event, PoliciesReady):
        return _after_load(state), ()

    if isinstance(event, SetPolicyB) and state.screen is Screen.menu:
        return replace(state, policy_b=event.policy), ()

    if isinstance(event, SetMode) and state.screen is Screen.menu:
        return replace(state, mode=event.mode), ()

    if isinstance(event, ConfirmStart) and state.screen is Screen.menu:
        return _begin_match(state, 0)

    if isinstance(event, MatchOver) and state.screen in (Screen.match, Screen.paused):
        score_a = state.score_a + (1 if event.winner == "a" else 0)
        score_b = state.score_b + (1 if event.winner == "b" else 0)
        return replace(state, screen=Screen.end, score_a=score_a, score_b=score_b), ()

    if isinstance(event, TickDt) and state.screen is Screen.match:
        period = 1.0 / state.tick_rate
        acc, n = consume(state.acc, event.dt, period)
        nxt = replace(state, acc=acc)
        return nxt, ((RequestTick(),) if n else ())

    if not isinstance(event, Key):
        return state, ()

    alias = event.alias

    if state.screen is Screen.menu:
        if alias == "escape":
            return state, (QuitApp(),)
        return state, ()

    if alias == "escape":
        return _to_menu(state), ()

    if state.screen is Screen.end:
        if alias == "return":
            return _begin_match(state, state.match_index + 1)
        return state, ()

    if state.screen is Screen.match:
        if alias == "p":
            return replace(state, screen=Screen.paused), ()
        if alias == "r":
            return _begin_match(state, state.match_index + 1)
        if alias == "h":
            return replace(state, panel_visible=not state.panel_visible), ()
        if alias in MOVE_ALIASES and state.mode is MatchMode.human_vs_ai:
            return state, (PushAbsolute(direction_for(alias)),)
        return state, ()

    if state.screen is Screen.paused:
        if alias == "p":
            return replace(state, screen=Screen.match), ()
        if alias == "n":
            return state, (RequestTick(),)
        if alias == "r":
            return _begin_match(state, state.match_index + 1)
        if alias == "h":
            return replace(state, panel_visible=not state.panel_visible), ()
        if alias in MOVE_ALIASES:
            return state, ()
        return state, ()

    return state, ()
