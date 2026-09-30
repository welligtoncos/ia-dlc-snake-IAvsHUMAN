"""Accumulator: at most one tick, no debt (P-UI-ACC)."""

from __future__ import annotations

import pytest

from snake_vs_machine.ui.clock import consume


def test_consume_caps_at_one_tick() -> None:
    acc, n = consume(0.0, 0.5, 0.1)
    assert n == 1
    assert 0.0 <= acc <= 0.1


def test_consume_needs_a_full_period() -> None:
    acc, n = consume(0.0, 0.05, 0.1)
    assert n == 0
    assert acc == pytest.approx(0.05)


def test_consume_rejects_non_positive_period() -> None:
    with pytest.raises(ValueError):
        consume(0.0, 0.1, 0.0)
