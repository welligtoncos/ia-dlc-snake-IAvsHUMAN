# U4 UI — NFR Design Patterns

Patterns for `ui/` and the two UI scripts. No cloud, no `training` / `evaluation` imports, no vsync.

## Layering

```text
scripts/jogo.py  +  scripts/<fps>
        |
        v
ui/  (pygame, PyYAML, fonts)
        |
        v
services  ->  agents  ->  core (rng.ui_match_seed)
```

Text alternative: scripts call `ui`; `ui` calls `MatchService` and `build_agent`; new match seeds come only from `core/rng.py`. `ui` must not import `training` or `evaluation`.

- pygame lives in the pygame layer (`app`, `screens`, `render`, `pygame_keys`) and `scripts/`.
- `keys.py`, `config.py`, and the accumulator helper import **no** pygame (D54 item 8).
- `core/rng.py` is the only place a stream tag may be added (D48).

## Clock and frame budget (D53 / D54)

| Pattern | Rule |
| --- | --- |
| Display cap | `Clock.tick(60)` only; `set_mode` without a vsync flag |
| Simulation | At most one `MatchService.tick` per frame; accumulator `min(acc + dt, 1/tick_rate)` |
| Pause | Accumulator frozen; **N** runs one `tick`; movement aliases ignored |
| Late frame | Match slows down; no tick debt |

`dt` for the accumulator comes from the clock return value or a monotonic delta **inside `ui` only**. It never enters `ui_match_seed`.

## Text-surface cache (D55 item 1)

HUD and RF05 stub strings change far less often than 60 Hz.

- Keep a `pygame.Surface` (or a small dict of surfaces) for HUD lines and for the stub (`proposta` / `executada` / `vetado`).
- Rebuild a cached surface only when its **content tuple** changes (names, lengths, ticks left, stub fields, `panel_visible`).
- The board pane is redrawn every frame from `State` (P-UI-FROZEN: draw must not mutate `State`).
- FPS script: 600 frames, spectator Difícil vs Difícil, **panel visible**, so the cache is on the measured path.

## FPS measurement (D54 item 1, D55 item 1)

- Real window (never `SDL_VIDEODRIVER=dummy`).
- 600 frames; print mean and min FPS to stdout; process exit 0.
- Mean < 55 → **ALERTA** in `aidlc-docs/construction/u4-ui/benchmark.md`.
- pytest never asserts FPS.

## Fonts (D54 item 5, D55 item 2)

- Runtime: `importlib.resources` files under `snake_vs_machine/ui/fonts/` (TTF + OFL license).
- Audit copy: the same files under workspace `assets/fonts/`.
- `setuptools` package-data must include `ui/fonts/*`.
- Face chosen in Code Generation (OFL only).

## Key aliases (D55 item 3)

`keys.py` maps **names** → `Direction` (and named non-move commands).

| Alias | Meaning |
| --- | --- |
| `up` / `w` | N |
| `right` / `d` | E |
| `down` / `s` | S |
| `left` / `a` | W |
| `escape` `p` `n` `r` `h` `return` | BR-KEY-* |

The pygame layer owns `K_*` → alias. Helper tests never import pygame.

## Session and match seeds (D55 item 4)

| Step | Rule |
| --- | --- |
| `session_seed` **present** in YAML (including `0`) | Use that int |
| `session_seed` **absent** (missing key or missing file) | `secrets.randbits(31)` once at session start; print the value on stderr |
| Each match | `ui_match_seed(session_seed, match_index)` in `core/rng.py` |
| Stream | `SeedSequence([session_seed, 6_000_003, match_index])` then `integers(0, 2**31-1)` — same shape as `collection_seed` |

No `time.time()` as a seed. `secrets` is only the optional session bootstrap and is logged.

## Config and model paths (D54 item 6, D55 item 5)

- CLI: `--config` default `config.yaml` (CWD).
- `yaml.safe_load` only.
- Missing or invalid file → documented field defaults + stderr warning (P-UI-CFG).
- `models_dir` default `"models"`, resolved against `Path(config_path).resolve().parent`.
- Tree files: `{models_dir}/bc_depth{3,6,8}.joblib`.

## Fail-fast (D10 off)

| Situation | Behaviour |
| --- | --- |
| `pygame.init` / `set_mode` fails | Portuguese line on stderr; next line = SDL / exception text; `sys.exit(1)` (D55 item 6) |
| `ModelLoadError` | Erro-4 screen; reason/path/traceback on stderr only |
| Bad `--config` | Defaults + stderr; do not exit |
| Missing font resource | Should not happen if package-data is installed; if it does: stderr + pygame default font |
| Agent contract error | Propagates; no substitute action |

No retry of `set_mode`. Erro 4 is not used when there is no display.

## Test and quality gates

| Control | Pattern |
| --- | --- |
| Coverage | `snake_vs_machine.ui` in `source`; omit `ui/render.py`; `fail_under = 80` branch |
| mypy | strict on `ui/`; pygame 2.x bundled stubs; `ignore_missing_imports` only as recorded fallback |
| pytest | `keys` / `config` / accumulator without pygame; one `SDL_VIDEODRIVER=dummy` smoke |
| Hypothesis | P-UI-* under `tests/ui/` (`dev` / `full`) |
| Extra | `[ui]` = pygame + PyYAML; `dev` includes `[ui]`; exact pins in Code Generation |

## Security, scalability, availability

Not applied. Security Baseline off: local YAML via `safe_load`, no network. One window; no worker pool in the UI process. No uptime target.
