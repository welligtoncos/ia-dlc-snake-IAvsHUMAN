"""Board, HUD and explanation stub. Omitted from coverage (D54)."""

from __future__ import annotations

from typing import Any

import pygame

from snake_vs_machine.agents.tree import TreeExplanation
from snake_vs_machine.core.state import State
from snake_vs_machine.ui.explain_text import lines as explain_lines
from snake_vs_machine.ui.fonts import load
from snake_vs_machine.ui.policies import label
from snake_vs_machine.ui.session import MatchMode, SessionState

BG = (18, 18, 24)
GRID = (40, 40, 50)
SNAKE_A = (80, 200, 120)
SNAKE_B = (230, 140, 70)
FOOD = (240, 210, 70)
OBSTACLE = (90, 90, 110)
TEXT = (230, 230, 230)
HUD_BG = (28, 28, 36)

_cache: dict[str, tuple[object, pygame.Surface]] = {}
_font: pygame.font.Font | None = None


def _face() -> pygame.font.Font:
    global _font
    if _font is None:
        _font = load(16)
    return _font


def cached_text(
    key: str, content: object, text: str, color: tuple[int, int, int] = TEXT
) -> pygame.Surface:
    prev = _cache.get(key)
    if prev is not None and prev[0] == content:
        return prev[1]
    surface = _face().render(text, True, color)
    _cache[key] = (content, surface)
    return surface


def draw_board(
    surface: pygame.Surface, state: State, origin: tuple[int, int], cell_px: int
) -> None:
    ox, oy = origin
    for y in range(state.height):
        for x in range(state.width):
            rect = pygame.Rect(ox + x * cell_px, oy + y * cell_px, cell_px, cell_px)
            pygame.draw.rect(surface, GRID, rect, 1)
    for cell in state.obstacles:
        pygame.draw.rect(
            surface,
            OBSTACLE,
            pygame.Rect(ox + cell.x * cell_px, oy + cell.y * cell_px, cell_px, cell_px),
        )
    if state.food is not None:
        pygame.draw.rect(
            surface,
            FOOD,
            pygame.Rect(
                ox + state.food.x * cell_px, oy + state.food.y * cell_px, cell_px, cell_px
            ),
        )
    for snake, color in ((state.snake_a, SNAKE_A), (state.snake_b, SNAKE_B)):
        for cell in snake.body:
            pygame.draw.rect(
                surface,
                color,
                pygame.Rect(ox + cell.x * cell_px, oy + cell.y * cell_px, cell_px, cell_px),
            )


def _names(session: SessionState) -> tuple[str, str]:
    if session.mode is MatchMode.human_vs_ai:
        return "Jogador", label(session.policy_b)
    return label(session.policy_a), label(session.policy_b)


def draw_hud(
    surface: pygame.Surface,
    session: SessionState,
    state: State | None,
    explain: TreeExplanation | None,
    hud_x: int,
    height: int,
) -> None:
    pygame.draw.rect(surface, HUD_BG, pygame.Rect(hud_x, 0, surface.get_width() - hud_x, height))
    name_a, name_b = _names(session)
    if state is None:
        lines = [
            "Snake vs. Máquina",
            "Enter: jogar",
            "1/2/3: Fácil/Médio/Difícil",
            "Tab: espectador",
            "Esc: sair",
            f"Modo: {session.mode.value}",
            f"B: {label(session.policy_b)}",
        ]
        content: Any = tuple(lines)
        y = 16
        for i, line in enumerate(lines):
            surface.blit(cached_text(f"menu-{i}", content, line), (hud_x + 12, y))
            y += 22
        return
    ticks_left = state.max_ticks - state.tick
    hud_content = (
        name_a,
        name_b,
        state.snake_a.length,
        state.snake_b.length,
        ticks_left,
        session.score_a,
        session.score_b,
        session.screen.value,
    )
    lines = [
        f"{name_a}: {state.snake_a.length}  {'viva' if state.snake_a.alive else 'morta'}",
        f"{name_b}: {state.snake_b.length}  {'viva' if state.snake_b.alive else 'morta'}",
        f"Ticks: {ticks_left}",
        f"Placar: {session.score_a}–{session.score_b}",
    ]
    y = 16
    for i, line in enumerate(lines):
        surface.blit(cached_text(f"hud-{i}", hud_content, line), (hud_x + 12, y))
        y += 22
    if session.panel_visible:
        if explain is None:
            panel_lines: tuple[str, ...] = ("sem explicação",)
            stub_key: object = ("none",)
        else:
            panel_lines = explain_lines(explain)
            stub_key = panel_lines
        for i, line in enumerate(panel_lines):
            surface.blit(cached_text(f"stub-{i}", stub_key, line), (hud_x + 12, y))
            y += 22


def overlay_lines(session: SessionState, outcome_text: str) -> list[str]:
    return [outcome_text, "Enter: revanche", "Esc: menu"]
