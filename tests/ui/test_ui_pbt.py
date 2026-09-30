"""P-UI-* properties. P-UI-PAUSE / P-UI-STEP hit session.py only (D58)."""

from __future__ import annotations

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from hypothesis import given
from hypothesis import strategies as st

from snake_vs_machine.core.setup import new_match
from snake_vs_machine.core.state import CoreConfig, copy
from snake_vs_machine.ui.clock import consume
from snake_vs_machine.ui.erro4 import window_text
from snake_vs_machine.ui.keys import direction_for
from snake_vs_machine.ui.session import (
    Key,
    RequestTick,
    Screen,
    handle,
)
from tests.ui.test_session import _playing


@given(st.sampled_from([("up", "w"), ("right", "d"), ("down", "s"), ("left", "a")]))
def test_p_ui_map(pair: tuple[str, str]) -> None:
    a, b = pair
    assert direction_for(a) is direction_for(b)


@given(st.sampled_from(["w", "a", "s", "d", "up", "down", "left", "right"]))
def test_p_ui_pause(alias: str) -> None:
    state, _ = handle(_playing(), Key("p"))
    assert state.screen is Screen.paused
    nxt, cmds = handle(state, Key(alias))
    assert cmds == ()
    assert nxt.screen is Screen.paused


def test_p_ui_step() -> None:
    state, _ = handle(_playing(), Key("p"))
    _, cmds = handle(state, Key("n"))
    assert cmds == (RequestTick(),)


@given(st.floats(min_value=0.0, max_value=1.0), st.floats(min_value=0.0, max_value=0.5))
def test_p_ui_acc(acc: float, dt: float) -> None:
    period = 0.1
    new_acc, n = consume(acc, dt, period)
    assert n in (0, 1)
    assert 0.0 <= new_acc <= period


@given(st.sampled_from(["missing", "sklearn", "numpy", "schema"]))
def test_p_ui_err(reason: str) -> None:
    text = window_text(reason)
    assert "traceback" not in text.lower()


def test_p_ui_frozen() -> None:
    import pygame

    from snake_vs_machine.ui.render import draw_board

    pygame.display.init()
    surface = pygame.display.set_mode((480, 480))
    state = new_match(CoreConfig(), 0)
    before = copy(state)
    draw_board(surface, state, (0, 0), 24)
    assert state == before
    pygame.display.quit()
