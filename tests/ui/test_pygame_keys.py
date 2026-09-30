"""K_* → alias (imports pygame, no display)."""

from __future__ import annotations

import pygame

from snake_vs_machine.ui.pygame_keys import alias_for


def test_arrows_and_wasd() -> None:
    assert alias_for(pygame.K_UP) == "up"
    assert alias_for(pygame.K_w) == "w"
    assert alias_for(pygame.K_RETURN) == "return"
    assert alias_for(pygame.K_ESCAPE) == "escape"
    assert alias_for(0) is None
