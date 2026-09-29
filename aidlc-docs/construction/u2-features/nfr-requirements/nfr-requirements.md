# U2 Features — NFR Requirements

Scope: `core.features` (`extract_features`, `feature_names`, `FEATURE_SCHEMA_VERSION`). Reuses U1 queries.

## Applicability

| ID | Applies to U2 | Notes |
| --- | --- | --- |
| RNF01 | Yes | Python ≥ 3.13 (D37) |
| RNF02 | Partial | No clock in `extract_features`. U5 < 1 ms **includes this function** + `predict_proba` + `safety_mask` (D40) |
| RNF03 | Derived only | Three conservative floods per call; must stay cheap enough for U3 ≥ 1000 games/min |
| RNF04 | Yes | Deterministic: same `(state, id)` → same tuple |
| RNF05 | Yes | hints, ruff, pytest, Hypothesis (P-FEAT-*) |
| RNF06 | Schema only | `FEATURE_SCHEMA_VERSION` for U5 JSON; no model I/O here |
| RNF07 | Yes | No pygame / sklearn / joblib in `core/features.py` |
| RNF08 | Yes | English names |
| RNF09 | Yes | `flood_fill_count(..., limit=200)` only for `space_free_*` (D39) |
| RNF10 | Yes | This unit |
| RNF11 | N/A | Match length is U1 |

Security Baseline: disabled (D09) — N/A.  
Resiliency Baseline: disabled (D10) — N/A.  
Usability / availability / cloud scale: N/A (in-process pure function).

## Performance

| Item | Requirement |
| --- | --- |
| `extract_features` | Pure CPU; no `sleep`, no clock, no I/O |
| Flood | At most three `flood_fill_count` calls (one per relative action); skip flood when `danger_d = 1` |
| Occupancy | At most three conservative `next_occupancy` calls (reuse per direction for ray + flood) |
| Budget | Worst-case kickoff (0 obstacles, three floods to 200): `extract_features` ≤ **0.5 ms**. Record in `benchmark.md`. If over: **ALERTA** — do **not** fail pytest (D40) |
| Deferred opt | If ALERTA: one flood when all three landings share a region with ≥ 200 cells. **Do not implement in U2** (D40) |

## Reliability and correctness

| Item | Requirement |
| --- | --- |
| Purity | Does not mutate `state` |
| Preconditions | `ValueError` if dead snake or terminal match (D38) |
| Count isometry | `flood_fill_count` = `min(reachable, limit)` after rotate/mirror (D39); U1 test on constructed states |
| Golden / fairness | Kickoff `seed=0` vector and `A == B` (D39) |
| Consistency | `danger_d = 1 ⇔ dist_danger_d = 0`; `danger_d = 1 ⇒ space_free_d = 0` (D38) |
| Coverage | ≥ 80% **branch** of all `snake_vs_machine.core` after this unit (remove `omit`) |
| PBT | P-FEAT-DET, RANGE, ROT, MIRROR, DANGER-DIST, DANGER-SPACE, DEAD; generators filter terminal (D38) |

## Maintainability

Public symbols have type hints. `ruff check` clean. Tests under `tests/core/` (`test_features.py` + PBT).  
Hypothesis profiles unchanged (`dev` / `full`). Optional `mypy --strict` on `core/`.

## Explicit non-goals for U2

Multiprocessing, pygame, sklearn, model load, PT labels, 60 FPS measurement, hardening `reachable_cells` order (unused by features).
