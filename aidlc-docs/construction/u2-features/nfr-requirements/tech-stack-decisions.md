# U2 Features — Tech Stack Decisions

Inherits U1 (`pyproject.toml`). Product NFRs stay in `nfr-requirements.md`.

| Choice | Decision | Why |
| --- | --- | --- |
| Language | Python ≥ 3.13 | D37 |
| Module | `src/snake_vs_machine/core/features.py` | D28 |
| Vector | `tuple` of 20; no numpy inside `features.py` | D38 Q8=A |
| Queries | `is_fatal`, `next_occupancy`, `flood_fill_count` only | D33, D39 |
| Tests | `pytest`, `pytest-cov --cov-branch`, `hypothesis` | D34, D39 |
| Coverage | Drop `omit = ["*/features.py"]` in U2 CG | D30, D36 |
| Hypothesis | Same `dev`/`full` profiles as U1 | D34 |
| Schema | `FEATURE_SCHEMA_VERSION = 1` until a breaking vector change | D38 |
| Bench | Worst-case kickoff timing; ≤ 0.5 ms target; ALERTA if over; not a pytest fail | D40 |
| Shared flood | Document-only if ALERTA; not implemented in U2 | D40 |

## Dependency set

No new runtime dependency. Dev tools already in `[project.optional-dependencies] dev`.

`core/features.py` must not import `pygame`, `sklearn`, or `joblib`.

## Out

Gymnasium, training loops, TreeAgent load (U5 uses the version constant only).
