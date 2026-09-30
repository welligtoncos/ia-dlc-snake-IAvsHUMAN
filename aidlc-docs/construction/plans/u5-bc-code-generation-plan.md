# U5 Behavior Cloning — Code Generation Plan

**Unit**: `u5-bc`
**Type**: brownfield add-on — `agents/tree.py`, `training/`, fixture models, two new RNG streams
**This file is the only source of truth for U5 code generation.**

NFR Requirements / NFR Design were **skipped** (D27). Acceptance numbers live in the Functional Design and in `requirements.md`.

## Unit context

| Item | Value |
| --- | --- |
| Stories | Skipped; map is RF02/RF03 / D30 U5 → U5 |
| Implements | `TreeAgent`, `safety_mask`, `TreeExplanation`, collect / split / fit / DAgger, fixture models, D12 alert (100) |
| Depends on | U2 `extract_features` / `FEATURE_SCHEMA_VERSION`; U3 `ExpertAgent`, `RandomAgent`, `MatchService`, `evaluation.scoring`, `agents.registry` |
| Does not include | Portuguese erro 4 (U4); translating the payload (U7); 500-match product D12 / 40% vs expert / noise (U7 — the U5 D12 line is the 100-match **alert** only) |
| API / repository / frontend / database / deploy | **Skip** |

## Locked design (D50 + D52)

- Product trees: `max_depth` ∈ {3, 6, 8}, `min_samples_leaf=1`, `criterion="gini"`, `class_weight="balanced"`, fixed `random_state`
- Frozen test set is **never** used to pick a hyperparameter
- DAgger: 5 iterations; **all three** trees (mask off) vs expert, **alternating sides**; expert labels all three students' states into **one** train set; ~20 000 new rows per iteration (D52 item 3)
- Closing the unit **requires** the real trained models and the recorded metrics (D52 item 1)
- Before the full run: a **5% probe** of `train_bc.py`, timed and extrapolated in `benchmark.md` (D52 item 2)
- Collect / DAgger / batteries use `evaluation.batch` multiprocessing (D52 item 2)
- Expert vs random: expert **alternates NW/SE**; the expert's side is stored on every row (D52 item 4)
- `.npz`: `X, y, match_id, seed, tick, snake_index, pairing, dagger_iter` + metadata
- Mask tie: `straight` if in the tie, else agent stream
- `TreeExplanation`: `proposed`, `executed`, `vetoed`, `proba` (3 slots), `path` of `PathStep(..., feature_value, went_left)`
- `predict_proba` mapped via `classes_`; missing class → 0
- sklearn pin: exact version resolved here, compatible with `numpy==2.2.6`, written into `decisions.md` and every JSON
- `AgentSpec("tree", {"path", "safety_mask"})`
- `ModelLoadError(code="model_load", reason=missing|sklearn|numpy|schema)`
- New streams only in `core/rng.py`: collection `[batch, 4_000_003, pairing_code, match_index]`, DAgger `[batch, 5_000_003, iter, match_index]`
- Inference < 1 ms is **ALERTA only** (D40)
- No pygame, no clock in `agents/` or `training/`

## Paths (application code NEVER under `aidlc-docs/`)

```
src/snake_vs_machine/core/rng.py                 # modified (two new helpers)
src/snake_vs_machine/agents/tree.py              # new
src/snake_vs_machine/agents/registry.py          # modified ("tree")
src/snake_vs_machine/agents/__init__.py          # modified
src/snake_vs_machine/training/__init__.py        # new package
src/snake_vs_machine/training/{dataset,collect,fit,dagger}.py
scripts/train_bc.py
scripts/bc_latency.py
models/fixtures/{two_class,tiny_depth3}.joblib + .json
pyproject.toml                                   # sklearn + joblib pin; coverage/mypy + training

tests/core/test_rng.py                           # two new composition locks
tests/agents/{test_tree,test_tree_pbt,test_registry}.py
tests/training/{test_dataset,test_collect,test_fit,test_dagger}.py
tests/evaluation/test_acceptance.py              # BC vs random reduced + slow
```

Docs only: `aidlc-docs/construction/u5-bc/code/code-generation-summary.md`
Bench: `aidlc-docs/construction/u5-bc/benchmark.md`

## Execution steps

- [x] **Etapa 1 — Pin sklearn (D50 item 8)**: in the project venv, `pip install "scikit-learn" "joblib"` and confirm import works with `numpy==2.2.6`. Record the exact `scikit-learn==X.Y.Z` (and `joblib==…`) in `pyproject.toml` **main** dependencies and as **D51** in `decisions.md`. Do not start tree code before the pin exists. If the resolver picks a build that cannot import, try the previous minor and record why.
- [x] **Etapa 2 — Tooling**: coverage `source` and mypy `files` gain `snake_vs_machine.training`. Add `sklearn` / `joblib` typing notes (mypy: ignore missing sklearn stubs **or** add the stub extra if it installs cleanly — pick one and write it in the summary). Re-run the existing suite: still green, marker-strict.
- [x] **Etapa 3 — RNG streams**: add `collection_seed(batch, pairing_code, match_index)` and `dagger_seed(batch, iteration, match_index)` to `core/rng.py` with tags `4_000_003` and `5_000_003`. Extend `tests/core/test_rng.py` with composition + golden-draw locks, same style as the four existing streams. Existing U1–U3 draws must stay unchanged.
- [x] **Etapa 4 — Tree tests first**: `tests/agents/test_tree.py` against **fixture** models (built in this step with a few dozen rows, committed under `models/fixtures/`):
  - `from_joblib` happy path
  - `ModelLoadError` for missing file, sklearn mismatch, numpy mismatch, schema mismatch
  - `ValueError` on dead / terminal
  - mask off: `executed is proposed`, `vetoed` is False
  - worked example 1 (wall-bound `straight` → `turn_right` when mask on)
  - worked example 2 (`straight` wins a proba tie)
  - worked example 3 (left/right tie is deterministic given the tick stream)
  - all-fatal keeps `proposed`, `vetoed` False
  - **D50 item 7**: fixture trained **without** one action → that `proba` slot is 0
  - `path` steps satisfy `went_left == (feature_value <= threshold)`
  - `act` equals `decide(...).action`; no `last_explanation` attribute
  **Run and show they fail** before `tree.py` exists (load tests can fail on import).
- [x] **Etapa 5 — `agents/tree.py`**: `ModelLoadError`, `ModelMeta`, `PathStep`, `TreeExplanation`, `_map_proba`, `_apply_mask`, `_path_steps`, `from_joblib`, `decide`, `act`. Make Etapa 4 green.
- [x] **Etapa 6 — Registry**: `AgentSpec("tree", {"path": ..., "safety_mask": ...})` → `TreeAgent.from_joblib`. Unknown-name test now lists `tree`. Pickle round-trip still holds. A worker can `build_agent` after `spawn`.
- [x] **Etapa 7 — Dataset**: `training/dataset.py` — write/read `.npz` with the D50 columns and metadata; `split_by_match` (sorted ids, 80/20). Tests: round-trip, disjoint `match_id`, metadata preserved, freeze (appending to train does not change test ids).
- [x] **Etapa 8 — Collect**: `training/collect.py` — equal match counts of expert vs expert (keep both snakes) and expert vs random (keep **whichever side the expert occupies**; alternate NW/SE per D25/D52 item 4; store `expert_side` on the row). Stop at `min_rows` (tests use a tiny `min_rows` and `max_ticks≈60`). Matches are distributed through `evaluation.batch` (`imap_unordered`, `cpu_count() - 1`); the worker is module-level and returns labelled rows, not just a `MatchResult`. Tests: every `y` equals `ExpertAgent.act` on that state (P-COL-EXPERT); `pairing` / `dagger_iter=0` / `expert_side` set correctly; seeds come from `collection_seed`.
- [x] **Etapa 9 — Fit**: `training/fit.py` — three depths, locked hyperparameters, `random_state=R` (`R=0` unless you veto). Writes `.joblib` + sibling JSON (versions, names, `random_state`). **Mandatory**: two fits on the same `(X, y)` produce identical trees. Fitting **must not** read the test split (assert in the test by not passing it in).
- [x] **Etapa 10 — DAgger (D52 item 3)**: `training/dagger.py` — 5 iterations. Each iteration: **all three** current trees (mask off) play against the expert through `evaluation.batch`, **alternating sides**; the expert labels the pre-tick states of **all three** students; new rows (~20% of the initial dataset, ≈ 20 000 on the full run; a small cap in unit tests) go into **one** train set; all three trees are refit. After each iteration record frozen-test accuracy and vs-random score (N=100 in the script, N=8 in the unit test). Test: test `match_id` set unchanged (P-DAG-FROZEN); `dagger_iter` in 1..5; three pairings written per iteration.
- [x] **Etapa 11 — PBT**: `tests/agents/test_tree_pbt.py` — P-TREE-ACTION, P-TREE-PURE, P-TREE-FROZEN, P-TREE-MASK-SAFE, P-TREE-MASK-KEEP, P-TREE-VETO, P-TREE-PROBA, P-TREE-PATH on `playing_state()` + the tiny fixture. Generated `CoreConfig` with `max_ticks≈60`.
- [x] **Etapa 12 — Acceptance tests**: reduced BC vs random (small N, fixture) in the default run. A `slow` test that **requires** `models/bc_depth6.joblib` asserts ≥ 90% over 500 (draw rate separate) and frozen-test ≥ 95% for 6 and 8 — this is part of closing, not of the default pytest. D12 100-match gap is recorded by the script (alert only).
- [x] **Etapa 13 — `scripts/`**: `train_bc.py` accepts a sample-fraction (1.0 full, 0.05 probe) and uses `evaluation.batch` for collect, DAgger and batteries. `bc_latency.py` measures kickoff `extract_features + decide` with mask on. Neither runs inside default pytest.
- [x] **Etapa 14 — Quality gates**: `ruff` clean; mypy strict green on `core` + `agents` + `services` + `evaluation` + `training`; `pytest --cov --cov-branch` ≥ 80% including `training`.
- [x] **Etapa 15 — 5% probe (D52 item 2)**: run `train_bc.py --fraction 0.05`, record wall time, extrapolate ×20 in `benchmark.md` **before** starting the full train. If the extrapolation is clearly worse than a night's run, stop and report — do not start the full train without saying so.
- [x] **Etapa 16 — Full Hypothesis**: `HYPOTHESIS_PROFILE=full` over the default suite (not `train_bc.py`). Record wall time.
- [x] **Etapa 17 — Full train + closing metrics (D52 item 1)**: run `train_bc.py --fraction 1.0`. Write `models/bc_depth{3,6,8}.joblib` + JSON. Record in `benchmark.md`: frozen-test accuracy per depth; DAgger curve (accuracy + vs-random per iteration); 500-match vs-random for BC-6 and BC-8 (draw rate separate); D12 100-match alert; real inference latency with mask on vs 1 ms. These numbers are the U5 closing bar.
- [x] **Etapa 18 — Markdown summary**: `aidlc-docs/construction/u5-bc/code/code-generation-summary.md`.
- [x] **Etapa 19 — Skipped layers**: API, repository, frontend, DB, deploy — N/A. The three real models sit in `models/` at the end of this unit (commit/tag `u5-done` only when you ask).

## Plan decisions you can veto at the gate

| Decision | Why | Alternative |
| --- | --- | --- |
| sklearn + joblib are **main** dependencies, not `[dev]` | U4 loads trees at runtime | Optional extra `[bc]` |
| `random_state = 0` | One documented integer; JSON records it | Another fixed int |
| Per-iteration vs-random N=100 in the script, N=8 in unit tests | Keeps pytest fast | Always 100 in tests |
| Probe fraction is exactly 0.05 of `min_rows` (5 000 of 100 000) | D52 says “~5%” | A different probe size |
| `evaluation.batch` grows a generic `run_imap(worker, tasks)` that collect/DAgger reuse | Avoids a second Pool implementation | Copy the Pool stanza into `training/` |
| mypy on `training/` | D49 spirit: every new package is typed | Leave `training` out of mypy until it hurts |
| Fixture trees committed under `models/fixtures/` | Tests must not call sklearn.fit in every session if we can avoid it; still allowed to fit once to create them | Build fixtures in `conftest.py` each run |

## Traceability

| Design source | Plan step |
| --- | --- |
| D50 items 1, 4 (hyperparams, `random_state`, two-fit identity) | 1, 9 |
| D50 item 2 (DAgger 5 + curve) | 10, 13, 17 |
| D50 item 3 (`.npz` schema) | 7, 8 |
| D52 items 1–4 (real models, 5% probe, 3-tree DAgger, expert side) | 8, 10, 15, 17 |
| D50 item 5 (mask tie) | 4, 5 |
| D50 item 6 (`TreeExplanation`) | 4, 5 |
| D50 item 7 (`classes_` / missing action) | 4, 5 |
| D50 item 8 (sklearn pin) | 1, 9 |
| D24 / D45 contracts | 4, 5, 6 |
| D40 1 ms ALERTA | 13, 15 |
| D27 D12 alert 100 | 12, 15 |
| D48 streams only in `rng.py` | 3 |
| PBT-02/03/07/08/09 | 11 |

## Out of this unit

U4 (Pygame, erro 4 PT); U7 (dictionary, 500-match product D12 / 40% vs expert / noise); `u5-done` tag — only after you approve the generated code **and** the closing metrics, and explicitly ask for the commit (which will include `models/bc_depth{3,6,8}.*`).
