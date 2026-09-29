# U1 Core — Code Generation Plan

**Unit**: `u1-core`  
**Type**: greenfield monolith (`src/snake_vs_machine/`, D28)  
**This file is the only source of truth for U1 code generation.**  
**Approved** with TDD-before-engine, PBT-from-`new_match`, replay identity, `fail_under=80` (D36).

## Unit context

| Item | Value |
| --- | --- |
| Stories | User stories skipped; map is RF/rules → U1 in `unit-of-work-story-map.md` |
| Implements | Rules 1–10, D25–D26, D29, D31–D35; `state`, `setup`, `engine`, `queries` |
| Depends on | None |
| Does not include | `features` (U2), agents, MatchService, UI, models |
| API / repo / frontend / DB / deploy | **Skip** (in-process library) |

## Locked design

- Frozen `State`/`Snake`/`CoreConfig`; `Cell` NamedTuple; `snake_a`/`snake_b`, `side_a`/`side_b`; `snake(id)` (D35)
- `next_occupancy(..., opponent_action=None)` (D33); `step` passes real opponent action
- Optional `_body_cells(state)` once per `step` (D35 suggestion)
- numpy **exact pin** (NEP 19 / D34); Hypothesis `dev`/`full`; `--cov-branch` ≥ 80%; bench informative
- No pygame / sklearn in `core/`

## Paths (application code NEVER under aidlc-docs/)

```
pyproject.toml
src/snake_vs_machine/__init__.py
src/snake_vs_machine/core/__init__.py
src/snake_vs_machine/core/state.py
src/snake_vs_machine/core/setup.py
src/snake_vs_machine/core/engine.py
src/snake_vs_machine/core/queries.py
tests/conftest.py
tests/core/test_state.py
tests/core/test_setup.py
tests/core/test_engine.py
tests/core/test_queries.py
tests/core/test_pbt.py
tests/core/test_random_matches.py
```

Docs only: `aidlc-docs/construction/u1-core/code/code-generation-summary.md`  
Bench fill: `aidlc-docs/construction/u1-core/benchmark.md`

## Execution steps

- [x] **Etapa 1 — Project structure**: distribution `snake-vs-machine`, import `snake_vs_machine`. Exact numpy pin. `fail_under = 80` + branch coverage in `pyproject.toml`. Dev: pytest, pytest-cov, hypothesis, ruff. `pip install -e .`.
- [x] **Etapa 2 — `core/state.py`**: enums, `Cell`, frozen `Snake`/`State`/`CoreConfig`, `copy`, `snake(id)`. No mutable collections (D35).
- [x] **Etapa 3 — `core/setup.py`**: `new_match`, D25/D26/D29, `SetupError`, SeedSequence (D31). Store only `side_a`/`side_b`.
- [x] **Etapa 4 — `core/queries.py`**: `next_occupancy`, `is_fatal`, `flood_fill_count`, `reachable_cells`. Optional `_body_cells`.
- [x] **Etapa 4b — Critical example tests first (TDD)**: write tests from `business-rules.md` — D32 ram `(5,5)`/`(6,5)`, head swap, D33 opponent tail with and without eat, H2H on food, simultaneous death. **Run and show they fail.** Do not implement `engine` before this.
- [x] **Etapa 5 — `core/engine.py`**: only after 4b is red. Pure `step` / `is_terminal` / `outcome` (D32–D35).
- [x] **Etapa 6 — Remaining example tests**: rules 1–10; D29 conservative `is_fatal`; D35 `hash` + `FrozenInstanceError`; 1800 ticks; replay identity (same seed + action sequence → identical states including food respawn).
- [x] **Etapa 7 — PBT**: Hypothesis draws `seed`, `obstacle_count`, and action sequences; apply `step` from `new_match` only — **never** hand-build arbitrary `State`. Profiles `dev`/`full`. Properties P-COPY, P-FATAL, P-OCC, P-OCC-CONSERV, P-ENG-*, P-SETUP-*.
- [x] **Etapa 8 — 1000 random matches**: helper (not `RandomAgent`); stream `[seed, 2000003]`.
- [x] **Etapa 9 — Quality config**: ruff; pytest-cov `--cov-branch` gate 80% on `core/{state,setup,engine,queries}`; `.hypothesis/` already gitignored.
- [x] **Etapa 10 — Informative bench**: fill `benchmark.md` (machine + mean `step` + games/min). Not a pytest fail.
- [x] **Etapa 11 — Markdown summary**: `aidlc-docs/construction/u1-core/code/code-generation-summary.md` (public APIs, how to test, D35 notes).
- [x] **Etapa 12 — Skipped layers**: API, repository, frontend, DB migrations, deploy artifacts — N/A for U1.

## Traceability

| Design / RF | Plan step |
| --- | --- |
| Regras 1–10, D14 | 5, 6 |
| D25–D26, D29 | 3, 6, 7 |
| D31 RNG | 1, 3, 8 |
| D32–D33 occupancy | 4, 5, 6, 7 |
| D34 NFR | 1, 7, 9, 10 |
| D35 frozen maps | 2, 6 |

## Out of this unit

`core/features.py` (U2 must drop coverage `omit`; see `u2-features-code-generation-plan.md`), agents, UI.
