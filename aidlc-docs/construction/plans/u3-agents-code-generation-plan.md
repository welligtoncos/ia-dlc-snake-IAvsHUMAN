# U3 Agents + MatchService — Code Generation Plan

**Unit**: `u3-agents`
**Type**: brownfield add-on — new packages `agents/`, `services/`, `evaluation/` plus a value-preserving refactor of U1 (D48 item 2)
**This file is the only source of truth for U3 code generation.**

## Unit context

| Item | Value |
| --- | --- |
| Stories | Skipped; map is agents + match loop → U3 in `unit-of-work-story-map.md` |
| Implements | `Agent` / `ExplainingAgent` protocols, `RandomAgent`, `ExpertAgent`, `HumanAgent`, `MatchService`, scoring, batch throughput; RF01/RF04/RF05 partially, RNF03 |
| Depends on | U1 `State`, `engine.step`, `engine.outcome`, `engine.is_terminal`, `setup.new_match`, `queries.{is_fatal, next_occupancy, flood_fill_count, next_head, in_bounds}`; U2 board transforms (tests only) |
| Does not include | `TreeAgent` / `safety_mask` (U5), `TimedAgent` / tournaments (U7), key codes / pacing (U4), trajectory persistence (U5) |
| API / repository / frontend / database / deploy | **Skip** — in-process library, no persistence, no network |

## Locked design

- `Agent` = `Protocol` with `act(state, snake_id) -> Action`; `ExplainingAgent` = `runtime_checkable` `Protocol` with `decide(state, snake_id) -> ActResult` (D45 item 1)
- Agent randomness only via `SeedSequence([seed, 3_000_003, tick, snake_index])`, `snake_index` explicitly 0 for A and 1 for B, built **lazily** (D46 item 8)
- Expert decision order of D44 item 1; food distance by **one** BFS from the food (D46 item 3); `flood_fill_count` capped at 200
- `HumanAgent` buffer of 2: a push onto a **full** buffer ignores the new command (D45 item 2)
- `MatchResult` has **no** `score_a`; scoring lives in `evaluation/scoring.py` (D48 item 5)
- Batch: `Pool.imap_unordered`, explicit `chunksize`, `cpu_count() - 1`, tasks carry `AgentSpec`s, worker at module level in `evaluation/batch.py` (D48 item 1)
- `core/rng.py` refactor is **value-preserving**: compositions unchanged, every U1/U2 test stays green
- Expert budget ≤ 1 ms is **ALERTA only**, never a pytest failure (D46 item 2, convention of D40)
- No pygame, no sklearn, no clock in `agents/` or `services/`

## Paths (application code NEVER under `aidlc-docs/`)

```
src/snake_vs_machine/core/rng.py              # new
src/snake_vs_machine/core/setup.py            # modified (import stream)
src/snake_vs_machine/core/engine.py           # modified (import stream)
src/snake_vs_machine/agents/__init__.py       # new package
src/snake_vs_machine/agents/base.py
src/snake_vs_machine/agents/random_agent.py
src/snake_vs_machine/agents/expert.py
src/snake_vs_machine/agents/human.py
src/snake_vs_machine/agents/registry.py
src/snake_vs_machine/services/__init__.py     # new package
src/snake_vs_machine/services/match.py
src/snake_vs_machine/evaluation/__init__.py   # new package
src/snake_vs_machine/evaluation/scoring.py
src/snake_vs_machine/evaluation/batch.py
scripts/throughput.py                         # outside the installed package
scripts/expert_latency.py
pyproject.toml                                # modified

tests/core/test_rng.py                        # new
tests/core/test_random_matches.py             # modified (import stream)
tests/agents/{__init__.py,test_random_agent.py,test_human.py,test_expert.py,test_registry.py,test_agents_pbt.py}
tests/services/{__init__.py,test_match.py,test_match_pbt.py}
tests/evaluation/{__init__.py,test_scoring.py,test_batch.py,test_acceptance.py}
```

Docs only: `aidlc-docs/construction/u3-agents/code/code-generation-summary.md`
Bench: `aidlc-docs/construction/u3-agents/benchmark.md`

## Execution steps

- [x] **Etapa 1 — Baseline reference**: recorded 2026-09-29. `ruff` 2× E501 in tests (fixed later); `mypy` clean (18 files); `pytest` 143 passed in 2m13s, branch coverage 96.74%. `evaluation/batch.py` at 61% (no tests yet). Tree already contained the U3 packages from an earlier generation pass.
- [x] **Etapa 2 — `core/rng.py` registry (D48 item 2)**: create the module holding every stream tag (obstacles `[seed + k * 1_000_003, 0]`, food respawn `[seed, tick_after]`, U1 test helper `[seed, 2_000_003]`, agents `[seed, 3_000_003, tick, snake_index]`), the per-stream `Generator` helpers, and the documented note on the untagged food stream. Add `tests/core/test_rng.py` locking the four compositions against hard-coded expected draws, so a future edit that changes values fails loudly.
- [x] **Etapa 3 — Value-preserving refactor**: `core/setup.py`, `core/engine.py` and `tests/core/test_random_matches.py` stop building `SeedSequence` inline and import from `core.rng`. **Run the full U1 + U2 suite and show it green with no expected value changed** — that is the acceptance criterion of the refactor. Export nothing new from `core/__init__.py` beyond `rng` helpers actually used outside `core`.
- [x] **Etapa 4 — `pyproject.toml` (D46 items 4, 5, 9; D49 item 1)**: coverage `source` gains `snake_vs_machine.agents`, `.services` and `.evaluation`; mypy `files` gains the same three; declare the `slow` marker and exclude it from the default run. `evaluation` is included because D48 created it after D46 fixed the list (D49 item 1), so the 80% branch floor covers `evaluation/batch.py` too. Re-run the suite to confirm the default run stays fast and marker-strict.
- [x] **Etapa 5 — `agents/base.py`**: `Agent` and `ExplainingAgent` protocols, `ActResult` (frozen, slots), `ExplanationPayload` marker protocol, the fixed `_ACTIONS` order, and the explicit `SnakeId → 0/1` index map. Plus `agents/__init__.py` and `tests/agents/__init__.py`. No behaviour yet.
- [x] **Etapa 6 — RandomAgent tests first**: `tests/agents/test_random_agent.py` — safe choice when a non-fatal action exists, uniform draw among candidates, all-fatal fallback to the three actions, `ValueError` on dead snake / terminal state, determinism across fresh instances. **Run and show they fail.**
- [x] **Etapa 7 — `agents/random_agent.py`**: BR-RND-1..4 with the lazy `core.rng` draw. Make Etapa 6 green.
- [x] **Etapa 8 — HumanAgent tests first**: `tests/agents/test_human.py` — worked example 4 (chain of two turns), worked example 5 (**mandatory**: facing east, `↑ ← ↓` fast → buffer `[↑, ←]`, no reverse when drained), redundant drop, reverse drop, `_last_direction is None` acceptance, empty buffer → `straight`, exactly one command consumed per `act`. **Run and show they fail.**
- [x] **Etapa 9 — `agents/human.py`**: BR-HUM-1..11, capacity checked **before** validation. Make Etapa 8 green.
- [x] **Etapa 10 — Expert tests first**: `tests/agents/test_expert.py` — worked example 1 as the U3 **golden** (kickoff seed 0, snake A → `straight`, `stage = "ranked"`, `drawn = False`, plus the full evaluation table asserting the manually checked food distances **14 / 16 / 14** for `straight` / `turn_left` / `turn_right`, the flood tie at the 200 cap, and the final tie-break by `straight` preference — D49 item 3), worked example 2 (head-risk waiver when strictly longer, with the equal-length companion producing a different action), worked example 3 (`stage = "fallback_space"`), all-fatal → `straight` with `stage = "all_fatal"`, and the left/right draw marking `drawn = True`. Fix the exact coordinates of examples 2 and 3 here. **Run and show they fail.**
- [x] **Etapa 11 — `agents/expert.py`**: `ActionEvaluation`, `ExpertDecision`, `_food_distances` (single BFS from the food over integer indices, no cap), `_decide`, `act`. Decision order BR-EXP-7..14, short-circuit for the action landing on the food. Make Etapa 10 green.
- [x] **Etapa 12 — P-EXP-DIST oracle**: Hypothesis test comparing `_food_distances` against a per-landing BFS that uses that action's **own** `next_occupancy`, for every non-fatal landing. This is the test that backs the exactness argument in `business-logic-model.md`.
- [x] **Etapa 13 — MatchService tests first**: `tests/services/test_match.py` — P-MS-TICK oracle against `engine.step`, `decide` routing (called once per tick, payload reaches `on_tick` unchanged, action applied is `decide(...).action`), `ValueError` on terminal `tick`, `TypeError` naming agent **and side** for a non-`Action` return (U3-REL-1), agent exceptions propagating unchanged, `on_tick` firing exactly `ticks` times, `sides` honoured. **Run and show they fail.**
- [x] **Etapa 14 — `services/match.py`**: `MatchResult` (no `score_a`), `TickHook`, `_ask`, `_tick_with_results`, `tick`, `play`, `_result`. Plus `services/__init__.py`. Make Etapa 13 green.
- [x] **Etapa 15 — `evaluation/scoring.py` (D48 item 5)**: per-match 1 / 0.5 / 0 from `outcome`, win rate, **draw rate reported separately**; `tests/evaluation/test_scoring.py` with P-MS-SCORE (the two sides always sum to 1.0). Plus `evaluation/__init__.py`.
- [x] **Etapa 16 — `agents/registry.py` (D48 item 1)**: `AgentSpec` (name + parameters, picklable) and `build_agent(spec)`; unknown name raises `ValueError` listing the known names. `tests/agents/test_registry.py` asserts every spec round-trips through `pickle` and builds the expected type.
- [x] **Etapa 17 — `evaluation/batch.py` (D48 item 1)**: module-level worker taking `(spec_a, spec_b, config, seed, sides)`, plus the driver using `Pool.imap_unordered` with explicit `chunksize` and `processes = cpu_count() - 1`; a sequential path for comparison; order-independent aggregation with comparisons sorted by seed. `tests/evaluation/test_batch.py` implements P-MS-PARITY over ~20 seeds (D48 item 3) and stays fast.
- [x] **Etapa 18 — Property-based tests**: `tests/agents/test_agents_pbt.py` — P-AGT-ACTION, P-AGT-PURE, P-AGT-FROZEN, P-RND-SAFE, P-RND-SPREAD, P-EXP-SAFE, P-EXP-SPACE, P-EXP-HEADRISK, P-EXP-ROT (rotation keeps the action, skipping `drawn` decisions), **P-EXP-MIRROR** (mirroring swaps `turn_left` ↔ `turn_right` and keeps `straight`, skipping `drawn` decisions — D49 item 2), P-EXP-DET, P-HUM-CAP, P-HUM-CHAIN, P-HUM-FILTER, P-HUM-ONE, P-HUM-NOREV. `tests/services/test_match_pbt.py` — P-MS-TERM, P-MS-REPLAY, P-MS-HOOK. Generated `CoreConfig` with `max_ticks ≈ 60` (D46 item 7), reusing `playing_state()` and the U2 board transforms.
- [x] **Etapa 19 — Acceptance battery**: `tests/evaluation/test_acceptance.py` — reduced expert-vs-random battery (small N) in the default run, and the full **500-match** ≥ 95% battery marked `slow` and **single-process** (D48 item 3, BR-U3-ACC1/2).
- [x] **Etapa 20 — `scripts/`**: `throughput.py` (multiprocess matches/min for RNF03, plus single-process matches/min **and ticks/s**, plus expert-vs-expert and expert-vs-random with no floor) and `expert_latency.py` (worst case and mean per decision). Both print the numbers that go into `benchmark.md`; both guarded by `if __name__ == "__main__":` with the worker living in `evaluation/batch.py`.
- [x] **Etapa 21 — Quality gates**: `ruff` clean; `mypy` strict green on `core` + `agents` + `services` + `evaluation` (D49 item 1); `pytest --cov --cov-branch` ≥ 80% over the four packages.
- [x] **Etapa 22 — `benchmark.md`**: create `aidlc-docs/construction/u3-agents/benchmark.md` with the expert rows required by D48 item 4 (**worst case** = kickoff with `obstacle_count=0`; **typical** = mean per decision in expert vs expert), the throughput rows (multiprocess vs single-process, ticks/s, expert variants), and the 500-match acceptance result with the draw rate separate. OK / **ALERTA** against the 1 ms budget and the 1000 matches/min floor; pytest never fails on time.
- [x] **Etapa 23 — Full Hypothesis run**: `HYPOTHESIS_PROFILE=full` including `slow`: 164 passed in 9m35s, branch coverage 98.33%.
- [x] **Etapa 24 — Markdown summary**: `aidlc-docs/construction/u3-agents/code/code-generation-summary.md` — files created vs modified, tests, measured numbers, deviations if any.
- [x] **Etapa 25 — Skipped layers**: API, repository, frontend, database migrations, deployment artifacts — record as N/A for this unit.

## Plan decisions you can veto at the gate

| Decision | Why | Alternative |
| --- | --- | --- |
| The default pytest run excludes `slow` via `addopts` | U3-MNT-4/6 wants the default run fast; `addopts` makes it automatic | Leave it opt-out and require `-m "not slow"` by hand |
| Tests mirror the package: `tests/agents/`, `tests/services/`, `tests/evaluation/` | Matches the existing `tests/core/` convention | One flat directory |
| Two scripts (`throughput.py`, `expert_latency.py`) instead of one CLI with subcommands | Each produces an independent block of `benchmark.md` | Single `scripts/bench.py` |
| `core/rng.py` exposes one helper per stream, not a single generic function with a tag argument | A caller cannot accidentally pass the wrong tag | One generic `generator(tag, *parts)` |
| The expert golden is worked example 1, asserted as a full evaluation table | Mirrors U2's golden vector; catches silent ranking changes | Assert only the chosen action |

## Traceability

| Design source | Plan step |
| --- | --- |
| D44 expert order, RNG stream, human filtering, `services/` package | 5, 7, 9, 11, 14 |
| D45 `ExplainingAgent` / `ActResult`, full-buffer ignore | 5, 8, 9, 13, 14 |
| D46 items 1–9 (throughput, 1 ms ALERTA, single BFS, coverage, mypy, `max_ticks`, `slow`, lazy RNG, `scripts/`) | 4, 7, 11, 12, 18, 19, 20, 21, 22 |
| D48 item 1 multiprocessing + specs | 16, 17, 20 |
| D48 item 2 RNG registry | 2, 3 |
| D48 item 3 parallel parity + single-process battery | 17, 19 |
| D48 item 4 expert benchmark rows | 22 |
| D48 item 5 `evaluation/scoring.py` | 15 |
| D49 item 1 `evaluation` in coverage + mypy | 4, 21 |
| D49 item 2 P-EXP-MIRROR | 18 |
| D49 item 3 golden distances 14 / 16 / 14 | 10 |
| PBT-02/03/07/08/09 (blocking) | 12, 18 |
| BR-U3-ACC1..4 | 19, 20, 22 |

## Out of this unit

`TreeAgent`, `safety_mask`, feature persistence (U5); `TimedAgent`, tournaments (U7); Pygame, key codes, pacing (U4); the `u3-done` commit and tag — only after you approve the generated code and explicitly ask for it.
