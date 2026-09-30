"""Frame accumulator: at most one simulation tick per call (D53 / P-UI-ACC)."""

from __future__ import annotations


def consume(acc: float, dt: float, period: float) -> tuple[float, int]:
    """Return `(new_acc, n_ticks)` with `n_ticks` in {0, 1} and acc in [0, period]."""
    if period <= 0:
        raise ValueError("period must be positive")
    if dt < 0:
        dt = 0.0
    acc = min(acc + dt, period)
    if acc >= period:
        return acc - period, 1
    return acc, 0
