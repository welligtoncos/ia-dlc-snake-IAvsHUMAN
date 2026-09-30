"""Key aliases without pygame (D55 item 3)."""

from __future__ import annotations

import pytest

from snake_vs_machine.core.state import Direction
from snake_vs_machine.ui.keys import COMMAND_ALIASES, direction_for, is_known


def test_arrow_and_wasd_share_a_direction() -> None:
    assert direction_for("up") is direction_for("w") is Direction.N
    assert direction_for("right") is direction_for("d") is Direction.E
    assert direction_for("down") is direction_for("s") is Direction.S
    assert direction_for("left") is direction_for("a") is Direction.W


def test_unknown_movement_alias_raises() -> None:
    with pytest.raises(ValueError, match="unknown"):
        direction_for("escape")


def test_commands_are_known_but_not_directions() -> None:
    for alias in COMMAND_ALIASES:
        assert is_known(alias)
        with pytest.raises(ValueError):
            direction_for(alias)
