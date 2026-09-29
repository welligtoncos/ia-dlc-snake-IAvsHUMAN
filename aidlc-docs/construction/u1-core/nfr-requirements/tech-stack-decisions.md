# U1 Core — Tech Stack Decisions

Implementation defaults for code generation. Product NFRs stay in `nfr-requirements.md`.

| Choice | Decision | Why |
| --- | --- | --- |
| Language | Python 3.11+ | RNF01 |
| Package | `src/snake_vs_machine` + `pyproject.toml`, `pip install -e .` | D28 |
| Numerics / RNG | **Exact** `numpy` pin in `pyproject.toml` (NEP 19). Same string in U5 JSON and U7 reports | D31, D34 |
| UI | **Not** a U1 dependency | RNF07 |
| ML | **Not** a U1 dependency | U5 |
| Tests | `pytest`, `pytest-cov`, `hypothesis` | RNF05, D30, PBT partial |
| Lint | `ruff` | RNF05, D30 DoD |
| Coverage tool | `pytest-cov --cov-branch`; ≥ 80% **branches** on U1 core modules | D30, D34 |
| Hypothesis | Profiles `dev` (100) and `full` (1000), `deadline=None`; env `HYPOTHESIS_PROFILE`; `full` before `u1-done`; `.hypothesis/` gitignored | D11, D34 |
| Types | `State`/`Snake` frozen+slots; `Cell` NamedTuple; `body` tuple; occupancy/obstacles frozenset | D34 |
| Typing check | `mypy --strict` on `core/` **optional** | D34 |

## Dependency set for U1 install

Runtime: `numpy==<pinned>` (exact, chosen at U1 code generation; NEP 19)  
Dev: `pytest`, `pytest-cov`, `hypothesis`, `ruff`; `mypy` optional

`pygame`, `scikit-learn`, `joblib`, `matplotlib`, `pyyaml` are declared at repo level later; **U1 modules must not import them**.

## Out

Gymnasium, stable-baselines3, cloud SDKs.
