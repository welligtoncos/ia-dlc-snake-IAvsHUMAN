# U4 UI — Benchmark

## FPS (D54 item 1 / D55 item 1)

`python scripts/ui_fps.py` — 600 frames, spectator Difícil vs Difícil, RF05 panel visible, real window, `Clock.tick(60)`.

| Metric | Value | Gate |
| --- | --- | --- |
| mean FPS | **60.78** | OK (≥ 55) |
| min FPS | 21.74 | informative (one hitch; mean is the ALERTA line) |

Measured 2026-09-30 on this Windows box (pygame 2.6.1, SDL 2.28.4). pytest does not assert FPS.

## Pins (D57)

| Package | Version |
| --- | --- |
| pygame | 2.6.1 |
| PyYAML | 6.0.3 |
