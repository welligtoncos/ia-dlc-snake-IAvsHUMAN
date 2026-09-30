    # U4 UI — NFR Requirements Plan

    **Unit**: `u4-ui`
    **Prerequisite**: Functional Design approved (D53)
    **Next after this stage**: U4 NFR Design

    No application code in this stage. Fill every `[Answer]:` below. Do not answer in chat.

    ## Execution checkboxes

    - [x] Read U4 functional design (D53)
    - [x] Trace NFRs already locked (RNF01–RNF02, RNF04–RNF08, RNF11, D07, D09, D10, D28, D34, D37, D53)
- [x] Collect answers in this file (`[Answer]:` tags)
- [x] Resolve ambiguities — Q3=X and Q1/Q6 extras were fully specified; registered as D54
- [x] Write `aidlc-docs/construction/u4-ui/nfr-requirements/nfr-requirements.md`
- [x] Write `aidlc-docs/construction/u4-ui/nfr-requirements/tech-stack-decisions.md`
- [x] Present two-option NFR completion (next: U4 NFR Design)

    ## Locked (do not re-ask)

    | NFR / decision | U4 implication |
    | --- | --- |
    | RNF01 / D37 | Python ≥ 3.13; Windows, Linux, macOS |
    | RNF02 / D07 | Display loop **60 FPS**; `tick_rate` default 10 is display-only; headless never waits |
    | D28 / D53 Q8 | Clock lives only in `ui`; at most one `MatchService.tick` per frame; accumulator capped at one period |
    | D53 Q9 | Exact `pygame==X.Y.Z` pin is decided in **U4 Code Generation**, not here |
    | D53 Q10 | `cell_px` default 24; window derived; not resizable |
    | RNF04 | Match seed from `ui_match_seed` / `config.yaml` `session_seed`; no `time.time()` as seed |
    | RNF05 | hints, ruff, pytest, Hypothesis P-UI-* (PBT-08 under `tests/ui/`) |
    | RNF07 | pygame only in `ui/` and `scripts/jogo.py` |
    | RNF08 | English identifiers; Portuguese HUD / erro 4 / overlay |
    | RNF11 | Logical match length stays 1800 ticks |
    | D09 / D10 | Security Baseline and Resiliency Baseline **off** — no auth, no network SLA, no DR |
    | D34 | `numpy==2.2.6` unchanged; Hypothesis `dev` / `full` |
    | D48 | `ui` must not import `training` or `evaluation` |
    | D51 | sklearn / joblib pins unchanged |
    | D52 | Product models may miss play bars; U4 still loads `models/bc_depth{3,6,8}.*` |

    Inception lists `pyyaml` and `pygame` in the repo stack; neither is in `pyproject.toml` yet.

    ## Not applicable (no questions)

    - Horizontal scalability, multi-tenant load, cloud capacity (single local window)
    - Availability / failover (desktop process; quit is the recovery)
    - Audio, networking, accounts
    - Exact pygame version (D53 Q9)

    ---

    # Questions

    ## Question 1
    RNF02 asks for a stable 60 FPS. How is that verified?

    A) Design target only: `Clock.tick(60)` in the loop. No FPS number in pytest or `benchmark.md`

    B) Informative script (under `scripts/`) records mean FPS on a short spectator match; below 55 FPS writes **ALERTA** in `benchmark.md` and does not fail pytest (same convention as D40)

    C) Blocking: a default-suite test with `SDL_VIDEODRIVER=dummy` fails if mean FPS over a short spectator match is below 50

    X) Other (please describe after [Answer]: tag below)

    [Answer]: B — medido com display real (não com o driver dummy, que não desenha nada e daria números irreais).

    ## Question 2
    How should pygame enter the install graph? Training and headless batteries do not need SDL.

    A) Main `dependencies` (same as numpy / sklearn) — `pip install -e .` always pulls pygame

    B) Extra `[ui]`; the game and UI tests require `pip install -e ".[ui]"` (dev extra may include it)

    C) Dev extra only — the published package stays headless; `scripts/jogo.py` documents `.[dev]` or a one-off pygame install

    X) Other (please describe after [Answer]: tag below)

    [Answer]:B  

    ## Question 3
    mypy is strict on `core`, `agents`, `services`, `evaluation`, `training`. pygame has no first-party stubs.

    A) Add `ui/` to strict `files`; `ignore_missing_imports` for `pygame.*` (same pattern as sklearn)

    B) Add `ui/` to strict `files` and a pygame stub package as a **dev** dependency if it installs cleanly on this machine; otherwise fall back to A and record it

    C) Leave `ui/` out of mypy; only ruff + pytest apply there

    X) Other (please describe after [Answer]: tag below)

    [Answer]:X — Adicionar ui/ ao mypy strict. O pygame 2.x já distribui stubs de tipo dentro do próprio pacote; verificar na Code Generation. Só se o mypy não os reconhecer, usar ignore_missing_imports para pygame.* e registrar.   

    ## Question 4
    Coverage `source` today is core + agents + services + evaluation + training, `fail_under = 80` branch.

    A) Add `snake_vs_machine.ui` to `source` under the same 80% branch gate

    B) Add `ui` but omit `render.py` (pixel drawing) from coverage

    C) Keep the current `source` list; UI coverage is reported informatively and does not move `fail_under`

    X) Other (please describe after [Answer]: tag below)

    [Answer]:B

    ## Question 5
    How do default pytest tests touch pygame? CI and this Windows box may have no real display.

    A) Most tests import only `keys` / `config` / clock helpers (no `pygame` import). One smoke test sets `SDL_VIDEODRIVER=dummy` and opens a surface

    B) Every screen test uses `SDL_VIDEODRIVER=dummy` and a real `pygame.display` surface

    C) No pygame import in pytest at all. Helpers are pure; `scripts/jogo.py` is the only process that inits pygame

    X) Other (please describe after [Answer]: tag below)

    [Answer]:A

    ## Question 6
    Portuguese HUD / erro 4 need glyphs (`ã`, `í`, `ó`). pygame's default font is not guaranteed to have them.

    A) Bundle a small TTF in the repo and load it with `pygame.font.Font` (accents guaranteed)

    B) `SysFont` first; if the glyph is missing, fall back to the ASCII strings already listed in the FD (`nao`, `vitoria`, …)

    C) ASCII-only on screen (the FD table); no font file, no SysFont hunt

    X) Other (please describe after [Answer]: tag below)

    [Answer]:A — fonte com licença livre (por exemplo, DejaVu Sans ou Noto Sans, licença OFL), com o arquivo de licença commitado ao lado.

    ## Question 7
    Where is `config.yaml` resolved? RF10 / P-UI-CFG need a single rule.

    A) Current working directory only. Missing or invalid file → defaults + stderr warning

    B) CWD first; if missing, the directory of `scripts/jogo.py` (repo / install sibling)

    C) CLI argument `--config` with default `config.yaml` in the CWD; no second search path

    X) Other (please describe after [Answer]: tag below)

    [Answer]:C

    ## Question 8
    Display sync. D53 already caps simulation at one tick per frame.

    A) `set_mode` without vsync; `Clock.tick(60)` is the only cap

    B) Request vsync when this pygame build supports it, and still call `Clock.tick(60)`

    C) Uncapped `flip` (can exceed 60 FPS); simulation still follows `tick_rate` + D53 accumulator

    X) Other (please describe after [Answer]: tag below)

    [Answer]:A
