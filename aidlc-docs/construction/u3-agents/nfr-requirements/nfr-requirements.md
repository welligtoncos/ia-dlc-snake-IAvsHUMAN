# U3 Agents + MatchService — NFR Requirements

Decided by D46 (answers Q1–Q7 of `u3-agents-nfr-requirements-plan.md`).

## Applicability of project NFRs

| NFR | Applies to U3 | U3 requirement |
| --- | --- | --- |
| RNF01 | Yes | Python ≥ 3.13 (D37); no dependency beyond `numpy` in this unit |
| RNF02 | Indirectly | **No clock** in `agents/` or `services/`. Latency is measured by the `TimedAgent` wrapper in `evaluation` (D44 item 5) |
| RNF03 | **Yes, primary** | ≥ 1000 matches/min random vs random, required from the **multiprocess** run (D46 item 1); expert throughput recorded with no floor |
| RNF04 | No | Config file handling is U4 |
| RNF05 | Yes | Type hints on public APIs, ruff clean, pytest green, Hypothesis properties, mypy strict (D46 items 4–5) |
| RNF06 | No | Portuguese user-facing text is U4/U7 |
| RNF07 | Yes | `agents/` and `services/` import neither pygame nor sklearn |
| RNF08 | Yes | English identifiers throughout |
| RNF09 | Yes | `flood_fill_count(limit=200)` for space; food distance is a separate uncapped BFS (D44/D46) |
| RNF10 | No | Feature vector belongs to U2 |

## Performance requirements

| ID | Requirement | Type |
| --- | --- | --- |
| U3-PERF-1 | ≥ 1000 matches/min, random vs random, **multiprocess** | **Blocking** (RNF03) |
| U3-PERF-2 | Single-process matches/min **and ticks/s** recorded alongside it; ticks/s is the stable figure because it does not depend on match length (D46 item 1) | Informative |
| U3-PERF-3 | `ExpertAgent` decision ≤ **1 ms** worst case; exceeding it records **ALERTA** in `benchmark.md` and does **not** fail pytest (D46 item 2, same convention as D40) | Informative with ALERTA |
| U3-PERF-4 | Expert-vs-expert and expert-vs-random throughput measured and recorded, no floor (D17) | Informative |
| U3-PERF-5 | Food distance costs **one** BFS per decision, not three (D46 item 3) | Design constraint |

### Baseline measured before implementation

Simulating the D44/D45 policy on U1 code (30 matches, `CoreConfig()`, seeds 0–29):

| Policy | Ticks/match | Matches/min | µs/tick |
| --- | --- | --- | --- |
| Uniform over three actions (U1 helper) | 12.9 | 22,921 | 203 |
| Safe random (BR-RND-1) | 433.4 | 812 | 171 |

Per-tick breakdown: `default_rng(SeedSequence([...]))` + one `integers` = 31.3 µs **per agent**; three `is_fatal` = 21.8 µs per agent; `engine.step` = 25.5 µs. The per-tick RNG construction is the largest single cost, ahead of the engine itself.

Consequence: the single-process figure starts **below** the RNF03 floor, which is why D46 item 1 requires the floor from the multiprocess run. The RNG cost is addressed by the lazy construction of D46 item 8 (Q8=A): the expert stops paying it entirely, the random agent still does.

## Reliability requirements

| ID | Requirement |
| --- | --- |
| U3-REL-1 | `MatchService` validates that each agent returned an `Action` and raises `TypeError` naming the agent and the side (D46 item 6). Contract violations fail loudly; they are never patched with a fallback action. |
| U3-REL-2 | `tick` on a terminal state raises `ValueError` (BR-MS-3). |
| U3-REL-3 | `act` on a terminal state or dead snake raises `ValueError` (BR-AGT-5). |
| U3-REL-4 | `play` terminates within `max_ticks` for any pair of agents (P-MS-TERM). |
| U3-REL-5 | Agent exceptions propagate unchanged; `MatchService` never swallows them. |

## Determinism requirements

| ID | Requirement |
| --- | --- |
| U3-DET-1 | Same `(agents, config, seed, sides)` → identical `MatchResult` (P-MS-REPLAY). |
| U3-DET-2 | Randomness only through `SeedSequence([seed, 3_000_003, tick, snake_index])`; never Python `hash()`, never a global RNG, never a clock (D31/D44). |
| U3-DET-3 | `numpy==2.2.6` stays exactly pinned (NEP 19), so streams are stable across machines. |
| U3-DET-4 | The 95% acceptance battery is deterministic under fixed seeds, which is what allows it to be a pass/fail pytest test (D46 item 8). |

## Maintainability and testing requirements

| ID | Requirement |
| --- | --- |
| U3-MNT-1 | Coverage `source` becomes `core`, `agents`, `services`, `evaluation`, keeping branch coverage with `fail_under = 80` (D46 item 4; `evaluation` added by D49 item 1, since D48 created the package after this list was fixed). |
| U3-MNT-2 | mypy strict extended to `agents/`, `services/` and `evaluation/` (D46 item 5, D49 item 1). |
| U3-MNT-3 | Hypothesis properties use generated `CoreConfig` with a small `max_ticks` (≈ 60), and keep `playing_state()` for state-level properties (D46 item 7). |
| U3-MNT-4 | Expert ≥ 95% vs random over 500 matches is a pytest test marked `slow`, excluded from the default run (D46 item 8). |
| U3-MNT-5 | Throughput and latency measurement lives in a top-level `scripts/` directory, outside the installed package; its numbers go to `aidlc-docs/construction/u3-agents/benchmark.md` (D46 item 9). The multiprocessing worker itself lives in `evaluation/batch.py`, because Windows `spawn` re-imports the module in the child (D48 item 1). |
| U3-MNT-6 | `pytest.ini` / `pyproject` declares the `slow` marker so the default run stays fast and strict about unknown markers. |

## Not applicable

Security Baseline and Resiliency Baseline extensions are disabled (D09/D10). No network, no persistence, no authentication, no multi-tenancy, no availability or disaster-recovery targets: U3 is an in-process pure-logic unit. Scalability is bounded by the single desktop machine; the only horizontal concern is the multiprocessing used for batch throughput.
