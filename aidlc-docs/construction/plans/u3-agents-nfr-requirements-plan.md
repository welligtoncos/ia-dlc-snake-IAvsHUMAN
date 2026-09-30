# U3 Agents + MatchService — NFR Requirements Plan

**Unit**: `u3-agents`
**Prerequisite**: Functional Design approved (D44, D45)

## Execution checkboxes

- [x] Read U3 functional design (D44, D45)
- [x] Trace NFRs already locked (RNF01–RNF03, RNF05, RNF07, RNF09, RNF10, D14b, D17, D30, D34, D37)
- [x] Raise the throughput risk introduced by the safe `RandomAgent` (see Question 1)
- [x] Collect answers Q1–Q7 in this file (`[Answer]:` tags)
- [x] Resolve ambiguities — Q2 and Q7 X answers were fully specified; registered as D46
- [x] Write `aidlc-docs/construction/u3-agents/nfr-requirements/nfr-requirements.md`
- [x] Write `aidlc-docs/construction/u3-agents/nfr-requirements/tech-stack-decisions.md`
- [x] **Question 8** answered A (lazy draw); folded into D46 as item 8
- [x] Present two-option NFR completion (next: U3 NFR Design)

No application code in this stage.

## Locked (not re-asked)

| NFR / decision | U3 implication |
| --- | --- |
| RNF01 / D37 | Python ≥ 3.13 |
| RNF02 | No clock anywhere in U3; latency measured by `TimedAgent` in `evaluation` (D44 item 5) |
| RNF03 / D17 | ≥ 1000 matches/min random vs random; expert throughput measured and recorded with no floor; multiprocessing permitted |
| RNF05 | Type hints on public APIs, ruff clean, pytest green, Hypothesis properties |
| RNF07 | `agents/` and `services/` must not import pygame or sklearn (the U5 `TreeAgent` is the only sklearn consumer) |
| RNF08 | English identifiers; Portuguese strings are U4/U7 only |
| RNF09 | `flood_fill_count(limit=200)` for space; the expert's food distance is a separate full-board BFS (D44) |
| D14b | Win rate 1 / 0.5 / 0; draw rate reported separately |
| D30 | DoD: ruff, pytest, hints, `decisions.md`, tag `u3-done` |
| D34 | `numpy==2.2.6` exact pin; `SeedSequence` streams, never Python `hash()` |
| D44 Q10 | Acceptance battery and throughput as scripts with reduced versions in pytest; full runs marked `slow` |
| D09 / D10 | Security Baseline and Resiliency Baseline disabled |

## Measured risk: RNF03 is currently **not** met

BR-RND-1 makes the `RandomAgent` **avoid fatal moves** (Q2=B), and BR-RNG-1 builds a fresh `SeedSequence` per agent per tick (D44 item 3). Both were measured on the existing U1 code, simulating the exact D44/D45 policy (30 matches, `CoreConfig()`, seeds 0–29):

| Policy | Ticks per match | Matches/min (single process) | µs per tick |
| --- | --- | --- | --- |
| Uniform over all three actions (U1's throwaway helper) | 12.9 | 22,921 | 203 |
| Safe random (BR-RND-1) | 433.4 | **812** | 171 |

A random agent that never walks into a wall survives ~34x longer, so the 25,500 games/min recorded in U1 does not transfer. **812 matches/min is below the RNF03 floor of 1000.**

Where the 171 µs per tick goes (20,000 repetitions each, kickoff state):

| Operation | Cost | Per tick (two agents) |
| --- | --- | --- |
| `default_rng(SeedSequence([...]))` + one `integers` | 31.3 µs | 62.6 µs |
| `SeedSequence([...])` construction alone | 15.2 µs | — |
| `SeedSequence(...).generate_state(1)` | 19.4 µs | — |
| Three `is_fatal` calls | 21.8 µs | 43.6 µs |
| `engine.step` (U1 benchmark) | 25.5 µs | 25.5 µs |

The per-tick RNG construction is the **largest single line item — about 37% of the tick**, more than the engine itself. Questions 1 and 8 decide what to do about it.

---

# Questions

## Question 1
Given the measurement above (812 matches/min single-process, floor 1000), how should RNF03 be met?

A) Optimize single-process in measured steps like D43 (starting with the RNG, Question 8) until the floor is cleared without multiprocessing

B) Use multiprocessing to clear the floor (D17 permits it), recording both numbers and leaving the single-process figure as documented context

C) Optimize single-process first and only fall back to multiprocessing if the floor is still out of reach

D) Accept the shortfall as informative **ALERTA** like D40 and revisit in U7, where the real batteries run

X) Other (please describe after [Answer]: tag below)

[Answer]: B — e reportar também ticks/s (single-process), que não depende da duração das partidas.

## Question 2
Should `ExpertAgent.act` have a per-decision latency budget? It costs three `next_occupancy`, three `flood_fill_count` and three full-board BFS distances per tick — heavier than `extract_features`, which needed the D43 round to reach 0.5 ms.

A) Yes, a budget of ≤ 1 ms per decision, informative with **ALERTA** like D40, recorded in `benchmark.md`

B) Yes, and blocking: the U3 DoD fails if the expert exceeds the budget

C) No explicit budget: the expert is bounded indirectly by the recorded expert-vs-expert throughput (D17 has no floor there)

X) Other (please describe after [Answer]: tag below)

[Answer]:  A — orçamento ≤ 1 ms com ALERTA; e calcular a distância à comida com UM único BFS a partir da comida (ver D46), não três.

## Question 3
Coverage gate for the new packages. Today `[tool.coverage.run] source = ["snake_vs_machine.core"]` with `fail_under = 80` branch.

A) Extend `source` to `core`, `agents` and `services` under the same ≥ 80% branch gate

B) Extend `source` but require ≥ 90% for `agents` and `services`, since they are pure logic with no I/O

C) Keep the gate on `core` only and report the new packages informatively

X) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 4
mypy is currently strict on `core/` only.

A) Extend strict mode to `agents/` and `services/` as well

B) Keep strict on `core/`; the new packages get the default (non-strict) settings

X) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 5
How should `MatchService` react to an agent that violates the contract — returns something that is not an `Action`, or raises?

A) Trust the protocol: no runtime validation, exceptions propagate to the caller unchanged

B) Validate the returned value is an `Action` and raise `TypeError` naming the offending agent and side

C) Defensive fallback: log nothing, substitute `straight` and keep the match running

X) Other (please describe after [Answer]: tag below)

[Answer]: B

## Question 6
Property-based tests in U3 run whole matches, which is much heavier than U1/U2 properties. How should the Hypothesis budget be controlled?

A) Reuse the `dev` (100) / `full` (1000) profiles, keeping generated matches short by capping the number of ticks the generator plays (as `playing_state()` already does with at most 16 steps)

B) Reuse the profiles but add a `max_ticks` override in the generated `CoreConfig` so even a full match is cheap

C) Add a third profile with a lower example count specifically for U3 properties

X) Other (please describe after [Answer]: tag below)

[Answer]: B — max_ticks pequeno (ex.: 60) nos CoreConfig gerados, mantendo também o gerador playing_state() para propriedades de estado.

## Question 7
Where do the acceptance and throughput scripts live? The repository has no script location yet.

A) A top-level `scripts/` directory, excluded from the package distribution

B) Console entry points declared in `pyproject.toml`, implemented inside the `evaluation` package (U7 territory, used early by U3)

C) pytest tests marked `slow` only — no separate scripts, the "script" is `pytest -m slow`

X) Other (please describe after [Answer]: tag below)

[Answer]: X — O aceite de 95% vira teste pytest marcado slow (é um aprovado/reprovado natural, e com seeds fixas é determinístico). A medição de throughput e latência fica em scripts/ (fora do pacote), porque produz números que vão para o benchmark.md.

## Question 8
Added after the measurement above, and still open. Building a `SeedSequence` per agent per tick costs **31.3 µs**, the largest single item in a 171 µs tick — more than `engine.step` (25.5 µs). D46 item 1 clears RNF03 through multiprocessing, so this is not blocking, but it wastes roughly a third of every tick. The `ExpertAgent` draws only on left/right ties; the `RandomAgent` draws on every tick.

A) Make the draw **lazy** (built only when a tie actually needs it) and otherwise keep the per-tick `SeedSequence` — this removes the cost from the expert entirely and leaves the random agent paying it

B) Lazy as in A, plus replace the random agent's draw with a small documented integer mixer (splitmix64 over `seed`, `tick`, `snake_index`): still deterministic, still no Python `hash()`, ~0.2 µs, but it is hand-rolled RNG code the project has to own and test

C) Lazy as in A, plus an optional injected `Generator` on `RandomAgent` used only by the throughput script (one per match), keeping the pure per-tick path as the default everywhere else

D) Leave it as designed: multiprocessing already meets the floor and purity is worth the 31 µs

X) Other (please describe after [Answer]: tag below)

[Answer]: A
