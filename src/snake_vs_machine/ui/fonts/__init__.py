"""Bundled OFL face (Noto Sans Regular) loaded via importlib.resources."""

from __future__ import annotations

import importlib.resources
from functools import lru_cache

import pygame

_FILE = "NotoSans-Regular.ttf"


@lru_cache(maxsize=4)
def load(size: int = 16) -> pygame.font.Font:
    traversable = importlib.resources.files(__package__).joinpath(_FILE)
    with importlib.resources.as_file(traversable) as path:
        return pygame.font.Font(path, size)
