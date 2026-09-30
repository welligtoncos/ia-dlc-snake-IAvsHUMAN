"""One dummy-SDL surface blit (D54 item 8)."""

from __future__ import annotations

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from snake_vs_machine.ui.screens import paint
from snake_vs_machine.ui.session import new_session


def test_menu_blit_on_dummy_display() -> None:
    pygame.display.init()
    pygame.font.init()
    surface = pygame.display.set_mode((760, 480))
    paint(surface, new_session(0), None, None, 24, 280, None)
    pygame.display.quit()
