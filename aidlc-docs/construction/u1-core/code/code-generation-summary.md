# U1 Core — Code Generation Summary

**Unit**: `u1-core`  
**Package**: distribution `snake-vs-machine`, import `snake_vs_machine` (D28, D36)  
**TDD**: critical engine tests written and shown red (`NotImplementedError`) before `engine` (D36)

## Public APIs (`snake_vs_machine.core`)

| Module | Symbols |
| --- | --- |
| `state` | `SnakeId`, `Side`, `Direction`, `Action`, `DeathCause`, `EndReason`, `Outcome`, `Cell`, `Snake`, `CoreConfig`, `State`, `copy`, `snake(id)` |
| `setup` | `new_match(config, seed, sides=None)`, `SetupError` |
| `engine` | `step(state, action_a, action_b)`, `is_terminal(state)`, `outcome(state)` |
| `queries` | `body_cells`, `next_occupancy`, `is_fatal`, `flood_fill_count`, `reachable_cells` |

`State` / `Snake` / `CoreConfig` are `frozen=True, slots=True`. No mutable `dict`/`list`/`set` inside those types. `hash(state)` works; field assign raises `FrozenInstanceError` (D35).

`step` calls `next_occupancy(..., opponent_action=real)`. `is_fatal` omits it (D33). Opponent current head is FATAL in `is_fatal`; ram without swap is `opponent_body` (D32).

## How to test

```text
pip install -e ".[dev]"
pytest
pytest --cov --cov-branch
set HYPOTHESIS_PROFILE=full
pytest tests/core/test_pbt.py
```

Profiles: `dev` (100 examples, default) and `full` (1000). `deadline=None`. DoD `u1-done` still requires `HYPOTHESIS_PROFILE=full` plus commit/tag when you ask — not done in this stage.

Coverage gate: `fail_under = 80` with branch coverage on `snake_vs_machine.core` (U1 still omits `features.py`; U2 plan must remove that omit). Last run: **49 passed**, **97%** branch coverage. Python floor is **3.13** (D37).

## D36 / TDD record

Critical tests in `tests/core/test_engine_critical.py` failed first (6× `NotImplementedError` on `step`; D35 hash test already passed). Engine implemented after that red run.

PBT builds states only via `new_match` + `step`. Hypothesis draws `seed`, `obstacle_count`, and action sequences. Replay: same seed + same actions → identical states including food respawn.

Random helper (not `RandomAgent`): `SeedSequence([seed, 2000003])`. 1000 matches, zero uncaught exceptions.

## Skipped in U1

API, repository, frontend, DB migrations, deploy, `core/features.py`, agents, UI, pygame, sklearn.

## Extension compliance

| Rule | Status | Note |
| --- | --- | --- |
| PBT-02 / 03 / 07 / 08 / 09 | Conform | Properties + generators from `new_match`; tests under `tests/core/` |
| PBT remaining | N/A | Advisory only |
| Security Baseline | N/A | Disabled |
| Resiliency Baseline | N/A | Disabled |
