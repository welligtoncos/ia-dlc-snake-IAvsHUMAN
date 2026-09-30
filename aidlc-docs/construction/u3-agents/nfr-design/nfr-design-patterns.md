# U3 Agents + MatchService — NFR Design Patterns

Patterns for `agents/`, `services/` and the batch layer. No cloud, no pygame, no sklearn, no clock.

## Purity and layering

- Agents read a frozen `State` and return values; nothing mutates input.
- Dependency direction, enforced by review: `core` ← `agents` ← `services` ← (`evaluation`, `training`, `ui`) ← `scripts`. Nothing lower imports anything higher. In particular `services` never imports `evaluation`, which is why scoring lives outside `MatchResult` (D48 item 5).
- `RandomAgent` and `ExpertAgent` are pure functions of `(state, snake_id)`; `HumanAgent` owns only its command buffer.
- No module in `agents/` or `services/` reads a clock or touches the filesystem.

## Single RNG registry (D48 item 2)

`core/rng.py` becomes the only place where a stream is defined:

| Stream | Composition | Owner |
| --- | --- | --- |
| Obstacles | `[seed + k * 1_000_003, 0]` | `core.setup` |
| Food respawn | `[seed, tick_after]` | `core.engine` |
| U1 random-match test helper | `[seed, 2_000_003]` | `tests/core/test_random_matches.py` |
| Agent draws | `[seed, 3_000_003, tick, snake_index]` | `agents/` |

Rules:

- The refactor is **value-preserving**: the compositions above do not change, they only stop being written inline. Determinism of existing matches, the golden vector and the replay tests must all stay green afterwards.
- New streams (U5, U7) may only be added in this file, so tags cannot silently collide.
- Documented fragility: the food stream carries no tag, so it is `[seed, tick_after]` while obstacles are `[seed_k, 0]`. They would collide if `tick_after` were ever `0`; it never is, because a respawn happens after a completed tick, so `tick_after >= 1`. The registry records this rather than leaving it implicit, and a tagged food stream is the natural fix the day determinism can be re-baselined.
- `snake_index` is written explicitly as 0 for A and 1 for B, never taken from the enum's `auto()` value.

## Lazy randomness (D46 item 8)

- `SeedSequence` construction measures 31.3 µs — more than `engine.step` at 25.5 µs.
- The helper is called only at the moment a draw is needed. `ExpertAgent` therefore pays nothing except on a left/right tie; `RandomAgent` pays once per tick by definition.
- No agent caches a `Generator` between ticks: that would make the result depend on call order instead of on the state.

## Expert cost control

| Pattern | Effect |
| --- | --- |
| One BFS from the food per decision, not three from the landings (D46 item 3) | Cuts the dominant cost; proven exact in `functional-design/business-logic-model.md` |
| `flood_fill_count` capped at 200 (RNF09) | Bounds the space test regardless of board emptiness |
| Integer-index BFS reusing the U1 technique (D43) | No `Cell` allocation per neighbour, no `in_bounds` per cell |
| Short-circuit: an action landing on the food skips the distance lookup | Distance is 0 by definition |
| Budget ≤ 1 ms per decision, **ALERTA** only (D46 item 2) | Informative; never fails pytest |

Benchmark rows required (D48 item 4):

| Row | Scenario |
| --- | --- |
| Worst case | Kickoff, `obstacle_count=0` |
| Typical | Mean per decision across expert vs expert matches |

## Throughput pattern (D48 item 1)

- `multiprocessing.Pool.imap_unordered` with an explicit `chunksize`, `processes = cpu_count() - 1`.
- The task is `(spec_a, spec_b, config, seed, sides)`. **Specs, not agent objects**: a spec is a name plus parameters, and the worker builds the agent locally. This keeps every task picklable and works under the Windows `spawn` start method, where the child re-imports modules instead of inheriting memory.
- The worker function lives at module level in an installed package — never inside a `scripts/` `__main__` block — for the same `spawn` reason.
- Aggregation is **order-independent**, which is what allows `imap_unordered`. Whenever results must be compared (sequential against parallel), they are sorted by seed first.
- Parallelism exists only for batches. `tick` and `play` remain strictly sequential and clock-free.

## Fail-fast, no resilience theatre

Resiliency Baseline is disabled (D10). The unit has no retries, no circuit breakers, no fallbacks:

| Situation | Behaviour |
| --- | --- |
| Agent returns a non-`Action` | `TypeError` naming the agent and the side (D46 item 6) |
| `tick` on a terminal state | `ValueError` |
| `act` on a dead snake or terminal match | `ValueError` |
| Agent raises | Propagates unchanged |
| Worker process dies | The `Pool` raises; the script fails loudly rather than reporting a partial battery |

## Determinism as a test pattern

| Control | Pattern |
| --- | --- |
| Replay | Same `(specs, config, seed, sides)` → identical `MatchResult` |
| Parallel parity (D48 item 3) | ~20 seeds sequential vs parallel produce identical results after sorting by seed |
| Expert rotation | Board rotation does not change the chosen action, except on drawn ties (D44 item 2) |
| Distance oracle | Single BFS from the food agrees with a per-landing BFS (P-EXP-DIST) |
| Acceptance | Expert ≥ 95% vs random over 500 matches, `slow` marker, **single-process** (D48 item 3) |

## Test quality and gates

| Control | Value |
| --- | --- |
| Coverage | Branch, `fail_under = 80`, source `core` + `agents` + `services` + `evaluation` (D46 item 4, D49 item 1) |
| Typing | mypy strict on `core`, `agents`, `services`, `evaluation` (D46 item 5, D49 item 1) |
| Hypothesis | `dev` / `full` profiles; generated `CoreConfig` with `max_ticks` ≈ 60 (D46 item 7) |
| Markers | `slow` declared in `pyproject.toml`, excluded from the default run |
| Bench | Informative rows plus ALERTA lines; never a `fail_under` on time |

## Security, availability, scalability

Not applied. Security Baseline disabled (D09): in-process code, no network, no persistence, no untrusted input. No availability or disaster-recovery target: a desktop game. Scalability is limited to batch parallelism on one machine.

```text
+-------------------+     +-------------------+
| agents (pure)     | <-- | services.match    |
| lazy tick RNG     |     | tick / play       |
+-------------------+     +-------------------+
          |                        |
          v                        v
+-------------------+     +-------------------+
| core (frozen)     |     | evaluation        |
| rng registry      |     | scoring / batch   |
+-------------------+     +-------------------+
                                   ^
                                   |
                          +-------------------+
                          | scripts (CLI)     |
                          +-------------------+
```

Text alternative: agents and services sit on the frozen core, which now owns the RNG registry; evaluation adds scoring and batching on top of services; scripts are a thin command-line layer over evaluation.
