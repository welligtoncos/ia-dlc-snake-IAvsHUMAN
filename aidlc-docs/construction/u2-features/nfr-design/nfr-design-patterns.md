# U2 Features — NFR Design Patterns

Patterns for `core.features` only. No cloud, pygame, or ML.

## Purity and layering

- `extract_features` reads frozen `State`; returns a new `tuple` of 20; never mutates input.
- Imports: stdlib + U1 `state` / `queries` only. No `numpy` in this module (callers may wrap). No pygame, sklearn, joblib.
- Occupancy is always conservative (`opponent_action` omitted).

## Count, not set (D39)

- `space_free_*` uses `flood_fill_count` only.
- `reachable_cells` with a `limit` is order-dependent and is **not** used here.
- `flood_fill_count` must equal `min(reachable_size, limit)` after isometries (U1 test).

## Latency (D40)

- Worst-case measure: kickoff, `obstacle_count=0`, all three directions flood to 200.
- Target: ≤ 0.5 ms per `extract_features`. Write machine + time in `benchmark.md`.
- Over target → **ALERTA** in that file. Pytest stays green.
- U5 < 1 ms path = this call + `predict_proba` + `safety_mask` (leaves ≥ 0.5 ms for tree + mask if U2 stays on budget).

## Deferred optimization (do not implement)

If ALERTA: when the three landing cells lie in one 4-connected open region of size ≥ 200, one `flood_fill_count` can fill all three `space_free_*` (each saturates at 1.0). Record the idea in `benchmark.md` notes only.

## Fail-fast

- Dead snake or terminal match → `ValueError` (D38). No fallback zero vector.

## Test quality

| Control | Pattern |
| --- | --- |
| Golden / fairness | D39 kickoff vectors; `pytest.approx` on floats |
| PBT | `new_match` + `step`; filter terminal; board rotate/mirror |
| Coverage | Drop `omit` of `features.py`; `--cov-branch` ≥ 80% of all `core/` |
| Hypothesis | Same `dev` / `full` as U1 |
| Bench | Informative + ALERTA line; not `fail_under` on time |

## Resilience / scale / security

Not applied (D09, D10).

```
+-----------------------------+
| extract_features            |
| is_fatal + occ + count      |
| tuple 20 + schema version   |
+-----------------------------+
```

Text alternative: features sit on U1 queries and emit a versioned tuple.
