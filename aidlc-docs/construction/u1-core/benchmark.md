# U1 Core — Benchmark (informative)

**Not a gate** (D34). Measured during U1 code generation. Do not fail CI on these numbers.

## Machine

| Field | Value |
| --- | --- |
| OS | Windows 11 (win32 10.0.26200) |
| CPU | AMD64 Family 25 Model 80 Stepping 0, AuthenticAMD |
| RAM | not queried (desktop workstation) |
| Python | 3.13.7 |
| numpy (pinned) | 2.2.6 |

## Results

| Metric | Value |
| --- | --- |
| Mean time per `engine.step` | 25.48 µs (2236 steps) |
| Random-helper matches per minute | ~25 500 (200 matches in 0.47 s) |
| Notes (obstacle_count, seeds, tick cap) | `obstacle_count=4`, seeds `0..199`, helper stream `[seed, 2000003]`, `max_ticks=1800` (matches ended by death) |
