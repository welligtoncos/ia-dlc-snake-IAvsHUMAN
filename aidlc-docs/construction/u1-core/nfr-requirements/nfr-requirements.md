# U1 Core — NFR Requirements

Scope: `core.state`, `core.setup`, `core.engine`, `core.queries`. No UI, no agents, no models.

## Applicability

| ID | Applies to U1 | Notes |
| --- | --- | --- |
| RNF01 | Yes | Runtime for the package and tests |
| RNF02 | Partial | No clock in `step`. Inferência < 1 ms and 60 FPS are U4/U5 |
| RNF03 | Derived only | 1000 games/min is U3 acceptance; U1 must not introduce sleeps or O(board²) per tick |
| RNF04 | Yes | `State.seed`; deterministic `new_match` / food streams (D31) |
| RNF05 | Yes | hints, ruff, pytest, Hypothesis (partial PBT) |
| RNF06 | No | Models are U5 |
| RNF07 | Yes | Hard: no pygame import in `core/` |
| RNF08 | Yes | English identifiers |
| RNF09 | Yes | `limit=200` on `flood_fill_count` / `reachable_cells` |
| RNF10 | No | Features are U2 |
| RNF11 | Yes | `max_ticks = 1800` |

Security Baseline: disabled (D09) — N/A.  
Resiliency Baseline: disabled (D10) — N/A.  
Usability / availability / cloud scale: N/A (local library).

## Performance

| Item | Requirement |
| --- | --- |
| `step` | Pure CPU; no `sleep`, no clock, no I/O |
| `new_match` with `obstacle_count=0` | Instant for tests; 100 retries only when obstacles fail connectivity |
| `flood_fill_*` | Cap 200 cells (RNF09) |
| Headless budget (design, not U1 gate) | A 1800-tick match must stay cheap enough that U3 can still hit ≥ 1000 random-vs-random games/min on a typical desktop |

## Reliability and correctness

| Item | Requirement |
| --- | --- |
| Purity | `step` does not mutate the input `State` |
| Repro | Same `(config, seed, sides)` → same kickoff `State`; food RNG `SeedSequence([seed, tick])` |
| Errors | `SetupError` after 100 obstacle attempts; no crash on terminal `step` |
| Coverage | ≥ 80% **branch** coverage of U1 core modules (`--cov-branch`, D34); keep ≥ 80% of all `core/` after U2 |
| PBT | P-COPY, P-FATAL, P-OCC, P-OCC-CONSERV, P-ENG-*, P-SETUP-* (D33) |

## Maintainability

Public functions have type hints. `ruff check` clean. Tests under `tests/` mirroring `core/` (PBT-08).  
Hypothesis `dev` / `full` (D34). Optional `mypy --strict` on `core/`. Benchmark file is informative only.

## Explicit non-goals for U1

Multiprocessing, pygame, sklearn, network, persistence, logging SLAs, 60 FPS measurement.
