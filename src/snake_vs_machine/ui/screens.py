"""Draw the current session. No game rules here (D58)."""

from __future__ import annotations

import pygame

from snake_vs_machine.agents.tree import TreeExplanation
from snake_vs_machine.core.state import State
from snake_vs_machine.ui import erro4, render
from snake_vs_machine.ui.session import Screen, SessionState


def paint(
    surface: pygame.Surface,
    session: SessionState,
    match_state: State | None,
    explain: TreeExplanation | None,
    cell_px: int,
    hud_width: int,
    overlay: str | None,
) -> None:
    surface.fill(render.BG)
    board_w = (match_state.width if match_state else 20) * cell_px
    height = surface.get_height()
    if match_state is not None and session.screen in (
        Screen.match,
        Screen.paused,
        Screen.end,
    ):
        render.draw_board(surface, match_state, (0, 0), cell_px)
    render.draw_hud(surface, session, match_state, explain, board_w, height)
    if session.screen is Screen.error4 and session.error_reason:
        text = erro4.window_text(session.error_reason)
        y = 40
        for i, line in enumerate(text.split("\n")):
            surface.blit(render.cached_text(f"err-{i}", text, line), (24, y))
            y += 28
    if overlay:
        y = height // 2
        for i, line in enumerate(render.overlay_lines(session, overlay)):
            surface.blit(render.cached_text(f"ov-{i}", overlay, line), (24, y))
            y += 24
    if session.screen is Screen.menu:
        render.draw_hud(surface, session, None, None, board_w, height)
