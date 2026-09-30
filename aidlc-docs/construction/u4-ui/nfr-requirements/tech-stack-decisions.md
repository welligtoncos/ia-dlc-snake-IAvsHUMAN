# U4 UI — Tech Stack Decisions

New third-party dependencies enter only through the `[ui]` extra (D54 item 2). Headless `pip install -e .` stays numpy / sklearn / joblib.

| Area | Decision | Source |
| --- | --- | --- |
| Language | Python ≥ 3.13 | D37 |
| Display | pygame (exact pin in U4 Code Generation) | D53 Q9 / D54 item 2 |
| YAML | PyYAML, `safe_load` only (exact pin in U4 Code Generation) | D54 item 2 |
| Install extra | `[project.optional-dependencies] ui = [pygame, pyyaml]`; `dev` **includes** the `ui` extra | D54 item 2 |
| Font | OFL TTF + license file in `assets/fonts/` (file picked in CG; DejaVu / Noto are acceptable) | D54 item 5 |
| Clock | `pygame.time.Clock.tick(60)`; no vsync flag on `set_mode` | D54 item 7 |
| Config | `argparse` `--config`, default `config.yaml` (CWD) | D54 item 6 |
| Seeds | `ui_match_seed` in `core/rng.py` only | D48 / D53 |
| Typing | mypy strict on `ui/`; pygame 2.x in-tree stubs first | D54 item 3 |
| Lint | ruff `py313` | U1 |
| Tests | pytest + Hypothesis; dummy SDL only in one smoke test | D54 item 8 |
| FPS bench | `scripts/` + real window; ALERTA if mean < 55 | D54 item 1 |
| Coverage | `ui` in `source`; omit `ui/render.py` | D54 item 4 |
| Forbidden here | `training`, `evaluation`, vsync, wall-clock seeds, second config search path | D48 / D54 |

## Why an extra instead of a main dependency

`train_bc.py`, DAgger, and the U3/U5 batteries do not open a window. Putting pygame and PyYAML in `[ui]` keeps `pip install -e .` free of SDL. `pip install -e ".[dev]"` pulls `[ui]` so the default developer install can run `scripts/jogo.py` and `tests/ui/`.

## Why pygame stubs are not a separate package first

pygame 2.x ships typing files inside the wheel. Code Generation checks that mypy resolves `import pygame` after the pin. A third-party stub extra is not added unless that check fails; then `ignore_missing_imports` is recorded (D54 item 3).

## Why `safe_load`

`config.yaml` is a local file the player may edit. `yaml.safe_load` rejects arbitrary Python objects. Security Baseline is still off (D09); this is a stack default, not an extension control.

## Judgement calls (veto at the gate)

| Call | Choice | Why |
| --- | --- | --- |
| Exact pygame / PyYAML versions | Deferred to U4 Code Generation | D53 Q9; same ritual as D51 |
| Which OFL face | Chosen in CG (must be OFL + license file beside the TTF) | D54 names the license and path, not the family |
| `safe_load` | Fixed here | Local YAML; no `FullLoader` |
| `assets/fonts/` at workspace root | Matches D54; not inside `src/` | Game data, not an importable package |
