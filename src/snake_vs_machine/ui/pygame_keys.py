"""pygame `K_*` → named aliases (D55 item 3)."""

from __future__ import annotations

import pygame

_TABLE: dict[int, str] = {
    pygame.K_UP: "up",
    pygame.K_DOWN: "down",
    pygame.K_LEFT: "left",
    pygame.K_RIGHT: "right",
    pygame.K_w: "w",
    pygame.K_a: "a",
    pygame.K_s: "s",
    pygame.K_d: "d",
    pygame.K_ESCAPE: "escape",
    pygame.K_p: "p",
    pygame.K_n: "n",
    pygame.K_r: "r",
    pygame.K_h: "h",
    pygame.K_RETURN: "return",
}


def alias_for(key: int) -> str | None:
    return _TABLE.get(key)
