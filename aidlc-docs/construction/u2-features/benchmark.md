# U2 Features — Benchmark

**Budget**: `extract_features` ≤ 0.5 ms worst case (D40). Informative in pytest — never fails the suite.
**Worst case**: kickoff, `obstacle_count=0`, three floods saturating at 200, snake A, 400 calls.

## Machine

| Field | Value |
| --- | --- |
| OS | Windows 11 |
| CPU | AMD64 Family 25 Model 80 Stepping 0, AuthenticAMD |
| Python | 3.13.7 |
| numpy | 2.2.6 |

## Measured steps

| Step | Change | Mean `extract_features` | Status vs 0.5 ms |
| --- | --- | --- | --- |
| Baseline | `free_cells` scanned per direction | 4.11 ms | ALERTA |
| D42 | `free_cells` arithmetic, once per call | 2.12 ms | ALERTA |
| D43 step 1 | `reachable_cells` BFS over integer indices, precomputed blocked grid, no `Cell` per neighbour | 0.543 ms | ALERTA |
| D43 step 2 | `danger` from `_blocked(state, landing, occ)`; no `is_fatal` in the loop | **0.415 ms** | **OK** |
| D43 step 3 | Shared flood (D40) | not implemented | target already met |

Cumulative: **4.11 ms → 0.415 ms** (~10x). Step 1 gave the bulk of it by removing per-neighbour `Cell` allocation and `in_bounds` calls from the BFS; step 2 removed three `next_occupancy` rebuilds (`is_fatal` builds its own).

## Stability

Five consecutive repetitions after step 2: 0.416, 0.476, 0.452, 0.423, 0.434 ms. All within budget, but the margin is ~15%, so a slower machine can cross 0.5 ms. Step 3 (shared flood) stays documented and unimplemented as the next lever.

## Deferred optimization (not implemented)

When the three landing cells share one 4-connected open region of size ≥ 200, a single `flood_fill_count` can fill all three `space_free_*` — each saturates at 1.0 (D40). Applicable only when the three occupancies coincide, i.e. no action lands on the food.
