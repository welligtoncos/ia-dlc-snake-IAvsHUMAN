# U1 Core — Logical Components

In-process modules only. No queues, caches, or infrastructure services.

## Runtime (application)

| Component | Role |
| --- | --- |
| `core.state` | `Cell`, `Snake`, `State`, `CoreConfig`, enums; `copy` / `snake(id)` |
| `core.setup` | `new_match`; obstacle/food streams; `SetupError` |
| `core.engine` | `step`, `is_terminal`, `outcome` — uses `next_occupancy(..., opponent_action=real)` |
| `core.queries` | `next_occupancy`, `is_fatal`, `flood_fill_count`, `reachable_cells` |

```
+---------------------------+
| setup -> state            |
| state -> engine, queries  |
| queries -> engine         |
+---------------------------+
```

Text alternative: setup writes State; engine and queries read State; engine calls queries.

## Test and quality (not shipped as game features)

| Component | Role |
| --- | --- |
| `tests/core/` | Example tests + Hypothesis (PBT-08) |
| Hypothesis profiles | `dev` / `full` via `HYPOTHESIS_PROFILE` |
| Coverage | `pytest-cov --cov-branch` on U1 core modules |
| Random-match helper | 1000 games; also feeds the informative bench |
| `benchmark.md` | Machine + mean `step` + games/min (D34, not a gate) |
| `ruff` | Lint DoD |
| `mypy` | Optional `--strict` on `core/` |

## Version recording (cross-unit)

| When | Where |
| --- | --- |
| U1 code gen | Exact `numpy==…` in `pyproject.toml` |
| U5 | Same numpy version **and** sklearn version in each model JSON |
| U7 | Same pins in `reports/stress_results.md` (and any bench tables) |

## Explicitly absent

Load balancers, message buses, circuit breakers, object stores, pygame clock, sklearn.
