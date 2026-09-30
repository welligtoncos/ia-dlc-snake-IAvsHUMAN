# U4 UI — NFR Requirements

Decided by D54 (answers Q1–Q8 of `u4-ui-nfr-requirements-plan.md`).

## Applicability of project NFRs

| NFR | Applies to U4 | U4 requirement |
| --- | --- | --- |
| RNF01 | Yes | Python ≥ 3.13; desktop window on Windows, Linux, macOS |
| RNF02 | **Yes, primary** | 60 FPS via `Clock.tick(60)`; `tick_rate` display-only; measured on a **real** window (D54 item 1) |
| RNF03 | No | Headless throughput is U3 / U7; the UI process is one match |
| RNF04 | Yes | `--config` + `session_seed` → `ui_match_seed`; no wall-clock seed |
| RNF05 | Yes | hints, ruff, pytest, Hypothesis P-UI-*, mypy on `ui/` (D54 items 3–4, 8) |
| RNF06 | Indirect | Models stay under `models/`; U4 only loads them |
| RNF07 | Yes | pygame only in `ui/` and `scripts/jogo.py` |
| RNF08 | Yes | Portuguese on-screen strings; English identifiers |
| RNF09 | Indirect | Flood limit is inside `core`; UI must not call a second flood |
| RNF10 | No | Feature vector is U2 |
| RNF11 | Yes | Overlay at 1800 ticks; UI does not change `max_ticks` |

## Performance requirements

| ID | Requirement | Type |
| --- | --- | --- |
| U4-PERF-1 | Display loop targets **60 FPS**. Cap is `pygame.time.Clock.tick(60)` only — no vsync flag (D54 item 7) | Design constraint |
| U4-PERF-2 | At most one `MatchService.tick` per frame; accumulator ≤ `1/tick_rate` (D53) | Blocking (logic) |
| U4-PERF-3 | Informative FPS script under `scripts/`, **real window** (not `SDL_VIDEODRIVER=dummy`). Mean FPS < **55** → **ALERTA** in `aidlc-docs/construction/u4-ui/benchmark.md`. pytest never fails on FPS (D54 item 1) | Informative with ALERTA |
| U4-PERF-4 | Tree inference budget stays D40 (< 1 ms with mask). A slow `act` may drop FPS; that is recorded by U4-PERF-3, not patched in the UI | Inherited |

## Reliability requirements

| ID | Requirement |
| --- | --- |
| U4-REL-1 | Missing or invalid `--config` path → documented defaults + stderr warning; no crash, no dialog (D54 item 6, P-UI-CFG) |
| U4-REL-2 | `ModelLoadError` → erro-4 screen; traceback only on stderr (D53) |
| U4-REL-3 | `MatchService` contract errors (`TypeError`, `ValueError`) propagate; the UI does not substitute an action |
| U4-REL-4 | Quit (window close or menu Sair) releases the display and exits with code 0 |

## Determinism requirements

| ID | Requirement |
| --- | --- |
| U4-DET-1 | Match seeds only from `ui_match_seed(session_seed, match_index)` in `core/rng.py` |
| U4-DET-2 | Same config + same session seed + same match index + same key stream → same `State` sequence (clock does not enter the seed) |
| U4-DET-3 | Key map is a pure function of keycode → `Direction` (P-UI-MAP) |

## Maintainability and testing requirements

| ID | Requirement |
| --- | --- |
| U4-MNT-1 | Coverage `source` gains `snake_vs_machine.ui`; `fail_under = 80` branch; **omit** `snake_vs_machine/ui/render.py` only (D54 item 4) |
| U4-MNT-2 | mypy strict `files` gain `src/snake_vs_machine/ui`. Use pygame 2.x bundled stubs; `ignore_missing_imports` for `pygame.*` only if mypy cannot see them, and record the fallback (D54 item 3) |
| U4-MNT-3 | Default pytest: helpers (`keys`, `config`, accumulator) import **no** pygame. One smoke test sets `SDL_VIDEODRIVER=dummy` and opens a surface (D54 item 8) |
| U4-MNT-4 | Hypothesis P-UI-* live under `tests/ui/` (PBT-08). Profiles stay `dev` / `full` |
| U4-MNT-5 | FPS measurement is a `scripts/` tool, not a pytest test (D54 item 1) |

## Usability requirements

| ID | Requirement |
| --- | --- |
| U4-USA-1 | On-screen Portuguese uses a bundled OFL TTF under `assets/fonts/` plus the license file beside it (D54 item 5). HUD / erro 4 / overlay may use the accented strings from the FD |
| U4-USA-2 | Window is not user-resizable; size from `cell_px` + `hud_width` (D53) |
| U4-USA-3 | `--config PATH` default `config.yaml` in the **current working directory** only — no second search path (D54 item 6) |

## Not applicable

Security Baseline and Resiliency Baseline are disabled (D09/D10). No network, no accounts, no availability target. Scalability is one local window. Exact `pygame==` and `PyYAML==` pins are Code Generation (D53 Q9; same extra as D54 item 2).
