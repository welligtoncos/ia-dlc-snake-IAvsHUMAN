# U3 Agents + MatchService — Tech Stack Decisions

No new third-party dependency. U3 inherits the U1/U2 stack.

| Area | Decision | Source |
| --- | --- | --- |
| Language | Python ≥ 3.13 | D37 |
| Packages added | `agents/` (existed in the plan, first code now) and `services/` — new package | D28 / D44 item 6 |
| Randomness | `numpy.random.SeedSequence` + `default_rng`, stream `[seed, 3_000_003, tick, snake_index]` | D44 item 3 |
| numpy | `numpy==2.2.6`, exact pin (NEP 19) | D34 |
| Queries reused | `is_fatal`, `next_occupancy`, `flood_fill_count` | D33 / D39 |
| New algorithm | Private integer-index BFS from the food in `agents/expert.py` (one per decision) | D46 item 3 |
| Agent contracts | `typing.Protocol`: `Agent.act` plus optional `ExplainingAgent.decide` | D45 item 1 |
| Concurrency | `multiprocessing` for batch throughput only, never inside `tick` or `play` | D17 / D46 item 1 |
| Typing | mypy strict on `core/`, `agents/`, `services/` | D46 item 5 |
| Lint | ruff, `target-version = "py313"` | U1 |
| Tests | pytest + pytest-cov (branch, `fail_under = 80` over `core`+`agents`+`services`) + Hypothesis (`dev`/`full`) + `slow` marker | D46 items 4, 7, 8 |
| Scripts | Top-level `scripts/`, excluded from the distribution | D46 item 8 |
| Forbidden here | pygame, scikit-learn, joblib, any clock read, any file I/O | RNF07 / RNF02 |

## Why no new dependency

The expert needs a shortest-path distance, which is the only genuinely new algorithm in U3. A graph library (`networkx`, `scipy.sparse.csgraph`) would add a dependency and a conversion cost per tick for a 400-cell 4-connected grid, where a hand-written BFS over integer indices is both faster and already proven in U1 (`_flood_indices`, D43). Multiprocessing uses the standard library.

## RNG cost, resolved

Per-tick `SeedSequence` construction costs 31.3 µs per agent — the single largest component of a tick, ahead of `engine.step` at 25.5 µs. Q8=A (D46 item 8) makes the construction **lazy**: the expert draws only to break a left/right tie, so it leaves the hot path; the random agent still pays once per tick, and RNF03 is met through multiprocessing. No hand-rolled mixer, no injected `Generator`.
