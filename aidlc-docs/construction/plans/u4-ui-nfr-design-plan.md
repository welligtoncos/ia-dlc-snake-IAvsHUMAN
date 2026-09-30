# U4 UI — NFR Design Plan

**Unit**: `u4-ui`
**Prerequisite**: NFR Requirements approved (D54)
**Next after this stage**: U4 Code Generation (Infrastructure Design skipped)

No application code in this stage. Fill every `[Answer]:` below. Do not answer in chat.

## Execution checkboxes

- [x] Read `u4-ui/nfr-requirements/{nfr-requirements,tech-stack-decisions}.md`
- [x] Map each NFR to a pattern or a logical component
- [x] Collect answers in this file (`[Answer]:` tags)
- [x] Resolve ambiguities — Q1/Q2/Q4/Q5/Q6 extras were fully specified; registered as D55
- [x] Write `aidlc-docs/construction/u4-ui/nfr-design/nfr-design-patterns.md`
- [x] Write `aidlc-docs/construction/u4-ui/nfr-design/logical-components.md`
- [x] Present two-option NFR Design completion (next: U4 Code Generation)

## Category assessment (rule requires all categories to be judged)

| Category | Applicable | Justification |
| --- | --- | --- |
| Performance patterns | **Yes** | RNF02 / D54: 60 FPS, real-window script, ALERTA < 55, one tick/frame |
| Scalability patterns | **No** | One local window; no load growth, no worker pool in the UI process |
| Resilience patterns | **Minimal** | Resiliency Baseline off (D10). Fail-fast: display init, `ModelLoadError`, contract errors. No retry |
| Security patterns | **No** | Security Baseline off (D09). Local `config.yaml` via `safe_load`; no network, no auth |
| Logical components | **Yes** | `ui/` modules, `scripts/jogo.py`, FPS script, `ui_match_seed` in `core/rng.py`, font/model paths |
| Availability / DR | **No** | Desktop process; quit is the recovery |
| Observability | **Minimal** | stderr warnings; FPS numbers → `benchmark.md`; no logging framework |

## Decided, not re-asked

| Item | Source |
| --- | --- |
| `Clock.tick(60)` only; no vsync | D54 item 7 |
| FPS script, **real** window; mean < 55 → ALERTA; pytest never fails on FPS | D54 item 1 |
| pygame + PyYAML in `[ui]`; `dev` includes `[ui]`; pins in Code Generation | D54 item 2 / D53 Q9 |
| mypy on `ui/`; pygame 2.x stubs; `ignore_missing_imports` only as recorded fallback | D54 item 3 |
| Coverage: `ui` in source, omit `render.py` | D54 item 4 |
| OFL TTF + license in `assets/fonts/` | D54 item 5 |
| `--config`, default `config.yaml` in CWD; missing/invalid → defaults + stderr | D54 item 6 |
| Helpers (`keys`, `config`, clock) import no pygame; one dummy-SDL smoke | D54 item 8 |
| `ui` does not import `training` or `evaluation` | D48 |
| New RNG streams only in `core/rng.py` | D48 |
| Existing tags 1_000_003 / 2_000_003 / 3_000_003 / 4_000_003 / 5_000_003 stay | `rng.py` |

---

# Questions

## Question 1
FPS script protocol (U4-PERF-3). The window must be real. What does the run look like?

A) 10 seconds, spectator **Médio vs Médio**, print mean and min FPS to stdout, always exit 0; numbers go into `benchmark.md` by hand

B) 600 frames (about 10 s at 60 Hz), spectator **Difícil vs Difícil** (mask on — heavier `act`), same print / exit / ALERTA rule

C) 10 seconds, spectator **Aleatório vs Aleatório** (cheap `act`, isolates render cost)

X) Other (please describe after [Answer]: tag below)

[Answer]: B — com o painel RF05 visível durante a medição.

## Question 2
How does the process find the OFL TTF at runtime? D54 places files under workspace `assets/fonts/`.

A) Walk up from `Path(__file__)` until `assets/fonts/<file>` exists (repo checkout). If not found: stderr + pygame default font (accents may break)

B) CWD `assets/fonts/` only (same rule as `--config` default). Missing font → stderr + pygame default font

C) Install the TTF as package data under `snake_vs_machine/ui/fonts/` **and** keep a copy (or symlink note) at `assets/fonts/` for the license audit trail

X) Other (please describe after [Answer]: tag below)

[Answer]:C — com o arquivo de licença OFL também incluído como package data, ao lado da fonte.

## Question 3
`keys.py` must be importable without pygame (D54 item 8). How are keycodes represented?

A) Documented integer constants in `keys.py` (the numeric values of `pygame.K_UP` / `K_w` / …). Tests pass those ints. A one-line adapter in the pygame layer translates `event.key`

B) `keys.py` exposes only `Direction` mapping from an opaque `int`; the pygame layer owns the table of `K_*` and is not imported by helper tests

C) Split: `keys.py` lists named aliases (`"up"`, `"w"`) for tests; pygame layer maps `K_*` → alias → `Direction`

X) Other (please describe after [Answer]: tag below)

[Answer]:C

## Question 4
`ui_match_seed(session_seed, match_index)` is new and may only be added in `core/rng.py`. Existing tags: 2e6+3, 3e6+3, 4e6+3, 5e6+3.

A) Tag **6_000_003**: `SeedSequence([session_seed, 6_000_003, match_index])` then `integers(0, 2**31-1)` — same shape as `collection_seed`

B) Tag **6_000_003**: use `[session_seed, 6_000_003, match_index]` directly as the `new_match` seed (no extra `integers` draw)

C) No new tag: `session_seed + match_index` is the match seed

X) Other (please describe after [Answer]: tag below)

[Answer]:A — e session_seed opcional no config.yaml: se ausente, sortear uma com secrets.randbits(31) no início da sessão e imprimir no stderr.

## Question 5
Where do tree `.joblib` paths resolve? Menu policies point at `models/bc_depth{3,6,8}.joblib`.

A) Relative to the **current working directory** (same as default `--config`)

B) Relative to the directory that contains the `--config` file (CWD if the default name is used)

C) Relative to the package / repo: walk up from `__file__` until `models/bc_depth3.joblib` exists

X) Other (please describe after [Answer]: tag below)

[Answer]: B — com uma chave models_dir no config.yaml (default "models"), resolvida em relação ao diretório do arquivo de config.

## Question 6
`pygame.display.set_mode` (or `pygame.init`) fails — no display, SDL error. Resiliency Baseline is off.

A) Portuguese line on stderr, process exit **1**. No erro-4 screen (that screen needs a display)

B) English exception text on stderr, exit 1 (keep PT for in-window errors only)

C) Retry `set_mode` once with a smaller size, then A

X) Other (please describe after [Answer]: tag below)

[Answer]:A — acrescentando, numa segunda linha, a mensagem técnica do SDL (em inglês) para diagnóstico.
