# U4 UI — Code Generation Plan

**Unit**: `u4-ui`
**Type**: brownfield add-on — new package `ui/`, two scripts, `core/rng.py` + small `services.match` surface
**This file is the only source of truth for U4 code generation.**
**Approved** with D58 (session machine before render).

## Unit context

| Item | Value |
| --- | --- |
| Stories | Skipped; map is Pygame UI → U4 in `unit-of-work.md` |
| Implements | RF01, RF04, RF07, RF09; RNF02 (60 FPS); erro 4 in PT; `scripts/jogo.py` |
| Depends on | U1 `State` / `new_match` / `Direction`; U3 `MatchService` / `HumanAgent` / `AgentSpec`; U5 `TreeAgent` / `ModelLoadError` / `TreeExplanation` / `models/bc_depth{3,6,8}.*` |
| Does not include | RF05 dictionary / path drawing (U7); `TimedAgent` / tournaments (U7); VIPER (U6); RF08 |
| API / repository / database / deploy | **Skip** — desktop process, no network |
| Frontend | **Yes** — Pygame screens (not web). `data-testid` **N/A** |

## Locked design

- D53 layout, keys, Esc/P/N/R/H, spectator any pair, erro 4, overlay, stub, 1 tick/frame, `cell_px` 24
- D54 extras `[ui]` (pygame + PyYAML), `dev` includes `[ui]`, coverage omit `render.py`, dummy smoke only, no vsync
- D55 text-surface cache, `importlib.resources` fonts, named key aliases, `ui_match_seed` + optional `secrets` session seed, `models_dir`, display-fail PT + SDL
- D56 stream characterization + tag invariants + `ui_match_seed` tests
- D58 `ui/session.py` pure TDD; P-UI-PAUSE/STEP on session; thin `app`/`screens`; session in coverage
- Exact pygame / PyYAML pins recorded as **D57** in Etapa 1 (D53 Q9)
- `ui` must not import `training` or `evaluation`

## Paths (application code NEVER under `aidlc-docs/`)

```
src/snake_vs_machine/core/rng.py                 # modified (D56 + ui_match_seed)
src/snake_vs_machine/services/match.py           # modified: public tick_with_results
src/snake_vs_machine/ui/__init__.py
src/snake_vs_machine/ui/config.py
src/snake_vs_machine/ui/keys.py
src/snake_vs_machine/ui/clock.py
src/snake_vs_machine/ui/policies.py
src/snake_vs_machine/ui/erro4.py
src/snake_vs_machine/ui/session.py               # D58
src/snake_vs_machine/ui/pygame_keys.py
src/snake_vs_machine/ui/fonts.py
src/snake_vs_machine/ui/render.py
src/snake_vs_machine/ui/screens.py
src/snake_vs_machine/ui/app.py
src/snake_vs_machine/ui/fonts/<ofl.ttf + LICENSE>
assets/fonts/<same bytes + LICENSE>
config.yaml                                      # example at workspace root
scripts/jogo.py
scripts/ui_fps.py
pyproject.toml                                   # extras, coverage, mypy, package-data

tests/core/test_rng.py                           # modified (D56)
tests/services/test_match.py                     # tick_with_results
tests/ui/__init__.py
tests/ui/test_keys.py
tests/ui/test_clock.py
tests/ui/test_config.py
tests/ui/test_policies.py
tests/ui/test_erro4.py
tests/ui/test_session.py                         # D58 TDD
tests/ui/test_ui_pbt.py
tests/ui/test_smoke.py                           # SDL_VIDEODRIVER=dummy
```

Docs only: `aidlc-docs/construction/u4-ui/code/code-generation-summary.md`  
Bench: `aidlc-docs/construction/u4-ui/benchmark.md`

## Execution steps

- [x] **Etapa 1 — Pins + tooling (D57)**: On this machine, install candidate pygame 2.x and PyYAML, record exact versions that import on Python 3.13. Add `[project.optional-dependencies] ui` and make `dev` include that extra. Coverage `source` += `snake_vs_machine.ui` with `omit` of `*/ui/render.py`. mypy `files` += `ui/`. Probe pygame 2.x bundled stubs; `ignore_missing_imports` for `pygame.*` only as a recorded fallback. `package-data` for `ui/fonts/*`. Re-run the existing suite (without UI tests yet) green. Register **D57** with the two pins.

- [x] **Etapa 2 — D56 + `ui_match_seed`**: Characterization test: `SeedSequence([5]).generate_state(4)` equals `SeedSequence([5, 0]).generate_state(4)` (measured **True** on this numpy). Rewrite the `rng.py` module docstring: trailing zeros are invisible; **vector length does not isolate streams**. Invariant test: the tag constants `{2_000_003, 3_000_003, 4_000_003, 5_000_003, 6_000_003}` are unique; document that `1_000_003` is the obstacle **stride** (not a position-2 tag); every counter that can sit in a tag-like slot (`tick_after` / `tick` ≤ `max_ticks`, `match_index` < 1_000_000) is **< 1_000_003**; new streams must put the tag in the **second** position. Add `ui_match_seed(session_seed, match_index)` as `SeedSequence([session, 6_000_003, match_index])` then `integers(0, 2**31-1)`, with composition + golden tests like `collection_seed`. Keep the food-stream note: `[seed, tick_after]` still must never use `tick_after == 0` (equals `[seed]` ≡ `[seed, 0]`). Existing U1–U5 rng tests stay green.

- [x] **Etapa 3 — `tick_with_results`**: Rename/export `_tick_with_results` as public `tick_with_results` in `services/match.py` (`tick` stays a one-liner). Test: explanations from `TreeAgent.decide` (fixture model) reach the caller; `tick` still returns only `State`. Needed so the HUD stub does not call `act` twice.

- [x] **Etapa 4 — `keys.py` (no pygame)**: Named aliases (`up`/`w`/… and commands `escape`/`p`/`n`/`r`/`h`/`return`). Tests: P-UI-MAP (pairs share a `Direction`); unknown alias raises. **Fail then implement.**

- [x] **Etapa 5 — `clock.py` (no pygame)**: `consume(acc, dt, period) -> (new_acc, n_ticks)` with `n_ticks ∈ {0, 1}` and `new_acc ∈ [0, period]` (P-UI-ACC). Pause is the caller's problem (do not call `consume`).

- [x] **Etapa 6 — `config.py` (no pygame)**: `safe_load`; `--config` default `config.yaml`; missing/invalid → defaults + stderr (P-UI-CFG); `models_dir` vs config parent; `session_seed` absent → `secrets.randbits(31)` + stderr (injectable rng in tests); present `0` is kept.

- [x] **Etapa 7 — `policies.py`**: `PolicyId` → label PT + `AgentSpec` (RF03 paths under resolved `models_dir`). Tests without loading joblib (spec shape only) plus one load of `models/bc_depth3.joblib`.

- [x] **Etapa 8 — `erro4.py`**: Title `Erro 4`; body lines per `reason` (`missing` / `sklearn` / `numpy` / `schema`); P-UI-ERR (no traceback in the window string).

- [x] **Etapa 9 — Fonts**: Vendor one OFL TTF that covers Portuguese (e.g. Noto Sans) into `src/snake_vs_machine/ui/fonts/` **and** `assets/fonts/`, license file beside both. `fonts.py` loads via `importlib.resources`.

- [x] **Etapa 10 — `pygame_keys.py`**: `K_*` → alias table only. Unit test imports pygame (no display).

- [x] **Etapa 11 — `session.py` (D58, TDD, no pygame)**: Write `tests/ui/test_session.py` **first** and show they fail. Then implement a pure machine: screen `menu` / `match` / `paused` / `end` / `error4`; session scoreboard; `match_index`; mode and policies. Inputs: key aliases + `dt`. Outputs: new state + commands (`push_absolute`, `tick_with_results`, load policies, quit). Mandatory cases: pause ignores movement; **N** while paused = exactly one tick command; **R** and **Enter** start a new match with `match_index + 1` (seed via `ui_match_seed`); **Esc** → menu; scoreboard accumulates across rematches and zeros on menu; error 4 from any screen → menu on any key.

- [x] **Etapa 12 — `render.py`**: Square cells; distinct colours; HUD + stub **text surfaces cached** until content tuple changes (D55). Coverage omit applies. P-UI-FROZEN tested by hashing/comparing `State` around a draw helper if extractable; otherwise a thin `draw_board` that takes a Surface.

- [x] **Etapa 13 — thin `screens.py` + `app.py` (D58)**: Translate pygame events → aliases, call `session`, execute commands, draw. Menu / match / overlay / erro 4. Display init failure = PT line + SDL line + `sys.exit(1)`. Human NW / tree SE.

- [x] **Etapa 14 — `scripts/jogo.py` + root `config.yaml`**: `python scripts/jogo.py [--config PATH]`. Example yaml with documented keys.

- [x] **Etapa 15 — Smoke**: `tests/ui/test_smoke.py` sets `SDL_VIDEODRIVER=dummy`, opens a surface, one menu blit. Default suite stays headless-safe.

- [x] **Etapa 16 — PBT**: `tests/ui/test_ui_pbt.py` — P-UI-MAP, P-UI-ACC, P-UI-FROZEN, P-UI-ERR, P-UI-CFG. **P-UI-PAUSE and P-UI-STEP hit `session.py` only** (no pygame). Profiles `dev` / `full`.

- [x] **Etapa 17 — `scripts/ui_fps.py`**: 600 frames, spectator Difícil vs Difícil, panel visible, real window, print mean/min FPS, exit 0. **Do not** put this in default pytest. If this machine has a display, run once and write `benchmark.md` (ALERTA if mean < 55); if not, record "not run — no display" and leave the script as the DoD vehicle.

- [x] **Etapa 18 — Quality gates**: `ruff` clean; mypy strict including `ui/` (and pygame stubs outcome recorded); `pytest --cov --cov-branch` ≥ 80% with `render.py` omitted. Existing U1–U5 tests stay green.

- [x] **Etapa 19 — Markdown summary**: `aidlc-docs/construction/u4-ui/code/code-generation-summary.md` — created vs modified, D57 pins, D56 test results, FPS row if measured.

- [x] **Etapa 20 — Skipped layers**: API, repository, database, deploy, web `data-testid` — N/A. Infrastructure Design already skipped.

## Plan decisions you can veto at the gate

| Decision | Why | Alternative |
| --- | --- | --- |
| Public `tick_with_results` | Stub needs `ActResult` without a second `decide` | Keep private and duplicate `_ask` in `ui` (worse) |
| FPS script named `ui_fps.py` | Matches `expert_latency.py` style | `scripts/fps.py` |
| One OFL face (Noto-class) | D55 requires OFL + license file, not a family | DejaVu if OFL copy is cleaner on disk |
| `secrets` injected in tests | P-UI-CFG must be deterministic | Patch `secrets.randbits` |

## Traceability

| Design source | Plan step |
| --- | --- |
| D53 screens / keys / overlay / 1 tick/frame | 4, 5, 13, 14 |
| D54 extra, coverage omit, dummy smoke, Clock only | 1, 15, 17 |
| D55 cache, fonts, aliases, session seed, models_dir, display fail | 6, 7, 9, 10, 12, 13 |
| D56 characterization + invariants + `ui_match_seed` | 2 |
| D58 session machine + TDD | 11, 16 |
| RF01 / RF04 / RF07 / RF09 | 11, 13, 14 |
| PBT-02/03/07/08/09 | 4, 5, 6, 8, 16 |
| RNF02 / U4-PERF-3 | 17 |

## Out of this unit

U7 dictionary and path drawing; U7 FPS/stress batteries beyond the 600-frame script; `u4-done` tag — only after you approve the generated code and explicitly ask for it.
