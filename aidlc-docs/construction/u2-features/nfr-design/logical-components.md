# U2 Features — Logical Components

In-process only. No queues, caches, or infrastructure services.

## Runtime (application)

| Component | Role |
| --- | --- |
| `core.features` | `extract_features`, `feature_names`, `FEATURE_SCHEMA_VERSION` |
| `core.queries` (U1) | `is_fatal`, `next_occupancy`, `flood_fill_count` |
| `core.state` (U1) | `State`, `SnakeId`, `Action`, `next_head` |

```
+-----------------------------+
| State -> extract_features   |
| features -> queries         |
| out: tuple + names + ver    |
+-----------------------------+
```

Text alternative: features read State, call queries, return a 20-tuple and schema version.

## Test and quality (not shipped)

| Component | Role |
| --- | --- |
| `tests/core/test_features.py` | Golden, fairness, examples, ValueError |
| `tests/core/test_pbt.py` (or features PBT module) | P-FEAT-* |
| `tests/core/test_queries.py` | Flood-count isometry (D39) |
| `benchmark.md` | Worst-case ms; ALERTA if > 0.5 ms (D40) |
| Coverage | All `core/` including `features.py` |

## Cross-unit

| When | Where |
| --- | --- |
| U2 CG | Implement features; drop coverage `omit`; fill `u2-features/benchmark.md` |
| U5 | Persist `FEATURE_SCHEMA_VERSION`; measure < 1 ms = features + proba + mask (D40) |
| U7 | PT labels of `feature_names()` only |

## Explicitly absent

Shared-flood cache (deferred D40), sklearn in `core/`, load balancers, message buses.
