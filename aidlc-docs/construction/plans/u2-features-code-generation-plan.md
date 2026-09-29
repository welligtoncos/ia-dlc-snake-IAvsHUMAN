# U2 Features — Code Generation Plan

**Unit**: `u2-features`  
**Type**: brownfield add-on to `src/snake_vs_machine/core/` (D28)  
**This file is the only source of truth for U2 code generation.**  
**Approved** with transform-helper tests and a separate U1 D39 commit (D41).

## Unit context

| Item | Value |
| --- | --- |
| Stories | Skipped; map is features 20 → U2 in `unit-of-work-story-map.md` |
| Implements | `extract_features`, `feature_names`, `FEATURE_SCHEMA_VERSION`; D19/D38/D39/D40 |
| Depends on | U1 `State`, `is_fatal`, `next_occupancy` (conservative), `flood_fill_count`, `next_head` |
| Does not include | agents, MatchService, UI labels, sklearn, shared-flood cache |
| API / repo / frontend / DB / deploy | **Skip** |

## Locked design

- 20-tuple + English `feature_names()`; `FEATURE_SCHEMA_VERSION = 1` (D38)
- `danger_*` = `is_fatal`; ray uses same conservative occupancy; `space_free_*` uses **count only** (D39)
- `ValueError` if dead or terminal; PBT filters those states (D38)
- Whole-board rotate/mirror (D38); `danger=1 ⇔ dist=0`; `danger=1 ⇒ space_free=0`
- Golden kickoff A + fairness A==B (D39)
- Drop coverage `omit` of `features.py`; ≥ 80% branch of **all** `core/`
- Bench worst-case ≤ 0.5 ms: ALERTA if over, pytest does not fail (D40)
- No numpy/pygame/sklearn in `features.py`
- Do **not** implement shared-flood (D40)

## Paths (application code NEVER under aidlc-docs/)

```
src/snake_vs_machine/core/features.py
src/snake_vs_machine/core/__init__.py
pyproject.toml
tests/core/test_features.py
tests/core/test_features_pbt.py
```

U1 already has isometry tests in `tests/core/test_queries.py` (D39, done).

Docs only: `aidlc-docs/construction/u2-features/code/code-generation-summary.md`  
Bench: `aidlc-docs/construction/u2-features/benchmark.md`

## Execution steps

- [x] **Etapa 0 — U1 D39 commit**: `flood_fill_count` contract + isometry tests (separate commit, message cites D39).
- [x] **Etapa 1 — TDD examples first**: write `test_features.py` (golden D39, fairness D39, ValueError D38, wall danger/dist/space). **Run and show they fail.** Do not implement `features.py` before this.
- [x] **Etapa 2 — `core/features.py`**: `extract_features`, `feature_names`, `FEATURE_SCHEMA_VERSION`. Algorithm in `business-logic-model.md`. Only `flood_fill_count` for space.
- [x] **Etapa 3 — Exports**: `core/__init__.py` public symbols.
- [x] **Etapa 4 — Remaining examples**: food diagonal, equal Manhattan, head_risk, consistency danger/dist/space.
- [x] **Etapa 5 — Transform helpers, then PBT**: first prove helpers — `rot90`×4 = identity; each mirror×2 = identity; kickoff `rot180` maps A body to B spawn and vice versa. Then PBT: `new_match` + `step` only; filter terminal; board transforms; P-FEAT-DET/RANGE/ROT/MIRROR/DANGER-DIST/DANGER-SPACE/DEAD.
- [x] **Etapa 6 — Coverage omit**: remove `omit = ["*/features.py"]` from `pyproject.toml`.
- [x] **Etapa 7 — Quality**: ruff; `pytest --cov --cov-branch` ≥ 80% of all `core/`.
- [x] **Etapa 8 — Bench**: worst-case kickoff timing in `benchmark.md`; ALERTA if > 0.5 ms; no pytest fail (D40).
- [x] **Etapa 9 — Markdown summary**: `aidlc-docs/construction/u2-features/code/code-generation-summary.md`.
- [x] **Etapa 10 — Skipped layers**: API, repository, frontend, DB, deploy — N/A.

## Traceability

| Design | Plan step |
| --- | --- |
| D38 schema / ValueError / geometry | 1–5 |
| D39 golden, fairness, count-only | 1, 2, 4 |
| D40 bench ALERTA | 8 |
| D30/D36 coverage all `core/` | 6, 7 |
| PBT-02/03/07/08/09 | 5 |

## Out of this unit

Agents, UI, `u2-done` tag (after you approve the code and ask for commit/tag). `HYPOTHESIS_PROFILE=full` before `u2-done`.
