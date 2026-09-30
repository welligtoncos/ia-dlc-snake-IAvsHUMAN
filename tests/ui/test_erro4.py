"""Erro 4 copy (P-UI-ERR)."""

from __future__ import annotations

import pytest

from snake_vs_machine.ui.erro4 import window_text


@pytest.mark.parametrize("reason", ["missing", "sklearn", "numpy", "schema"])
def test_each_reason_has_one_portuguese_body(reason: str) -> None:
    text = window_text(reason)
    assert text.startswith("Erro 4")
    assert "traceback" not in text.lower()
    assert "Traceback" not in text


def test_unknown_reason_raises() -> None:
    with pytest.raises(ValueError):
        window_text("other")
