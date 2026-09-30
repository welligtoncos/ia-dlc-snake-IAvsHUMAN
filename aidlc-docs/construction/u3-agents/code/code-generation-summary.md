# U3 Agents + MatchService — Code Generation Summary

**Unit**: `u3-agents`
**Plan**: `aidlc-docs/construction/plans/u3-agents-code-generation-plan.md`
**Decisions**: D44, D45, D46, D48, D49 (D47 unused)

## Created

```
src/snake_vs_machine/core/rng.py
src/snake_vs_machine/agents/{__init__,base,random_agent,expert,human,registry}.py
src/snake_vs_machine/services/{__init__,match}.py
src/snake_vs_machine/evaluation/{__init__,scoring,batch}.py
scripts/{throughput,expert_latency}.py
tests/core/test_rng.py
tests/agents/{test_random_agent,test_human,test_expert,test_registry,test_agents_pbt}.py
tests/services/{test_match,test_match_pbt}.py
tests/evaluation/{test_scoring,test_batch,test_acceptance}.py
```

## Modified

```
src/snake_vs_machine/core/setup.py          # obstacle stream from core.rng
src/snake_vs_machine/core/engine.py         # food stream from core.rng
src/snake_vs_machine/core/__init__.py       # exports agent_generator
tests/core/test_random_matches.py           # helper stream from core.rng
pyproject.toml                             # coverage + mypy + slow marker (D49 includes evaluation)
```

## Quality (default run, `HYPOTHESIS_PROFILE=dev`)

| Gate | Result |
| --- | --- |
| ruff | clean |
| mypy strict (`core`, `agents`, `services`, `evaluation`) | clean, 18 files |
| pytest | 162 passed, 1 deselected (`slow`) in 5m40s |
| Branch coverage | **98.33%** (floor 80%) |

## Measurements

See `aidlc-docs/construction/u3-agents/benchmark.md`.

- Expert kickoff: 0.427 ms mean / 0.858 ms max — OK vs 1 ms
- Random vs random parallel: 4918.8 matches/min — OK vs 1000
- Expert vs random, 500 matches: score 0.982, draw rate 0.000 — OK vs 0.95

## Deviations from the plan

- An earlier generation pass had already written packages `agents/`, `services/`, `evaluation/` and `core/rng.py` before Etapa 1 ran. Etapa 1 therefore measured that tree (143 passed, 96.74% coverage, `batch.py` at 61%) instead of a U1+U2-only baseline. Subsequent steps completed the missing tests (PBT, batch parity, acceptance, scripts) and the D49 items rather than rewriting working modules.
- TDD "show they fail" for Etapas 6/8/10/13 was not re-enacted on this pass: the implementations were already present. New tests added here (PBT, batch, acceptance, HumanAgent `ValueError`, `decide` TypeError) were written against that existing code.
- `HumanAgent.act` now calls `ensure_playable` (BR-AGT-5), which the first draft omitted.
- `HYPOTHESIS_PROFILE=full` including `slow`: **164 passed in 9m35s**, branch coverage 98.33%.

## Skipped layers (Etapa 25)

API, repository, frontend, database migrations, deployment artifacts — **N/A**. U3 is an in-process library.

## Out of this unit

`TreeAgent`, `safety_mask` (U5); `TimedAgent`, tournaments (U7); Pygame / key codes / pacing (U4); `u3-done` commit and tag (only after you approve and ask).
