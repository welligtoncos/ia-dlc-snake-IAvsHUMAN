# U5 Behavior Cloning — Business Rules

`_ACTIONS` stays `(straight, turn_left, turn_right)`.
`snake_index` is **0 for A, 1 for B**, written explicitly.

## TreeAgent contract

| ID | Rule |
| --- | --- |
| BR-TREE-1 | `TreeAgent` implements `ExplainingAgent`: `decide(state, snake_id) -> ActResult` and `act` returns `decide(...).action` (D45). |
| BR-TREE-2 | `act` / `decide` raise `ValueError` on a terminal state or a dead snake (BR-AGT-5). |
| BR-TREE-3 | No explanation is stored on the instance. The only copy is `ActResult.explanation` (D45). |
| BR-TREE-4 | `from_joblib(path, safety_mask=False)` reads `path` and the sibling JSON (`path` with suffix replaced by `.json`). |
| BR-TREE-5 | Missing `.joblib` or sibling JSON → `ModelLoadError(code="model_load", reason="missing")`. |
| BR-TREE-6 | Running sklearn version ≠ `ModelMeta.sklearn_version` → `reason="sklearn"`. Same for numpy (`"numpy"`) and `FEATURE_SCHEMA_VERSION` / `feature_names` (`"schema"`). |
| BR-TREE-7 | `ModelLoadError` messages are English and machine-readable. Portuguese erro 4 belongs to U4 (D50 Q8=A). |

## Prediction (D50 item 7)

| ID | Rule |
| --- | --- |
| BR-PROBA-1 | Raw `predict_proba` is mapped onto a 3-slot vector in `_ACTIONS` order through `tree.classes_`. |
| BR-PROBA-2 | A class absent from `classes_` gets probability **0**. The three slots still sum to 1 when at least one class was seen. |
| BR-PROBA-3 | `proposed` is `tree.predict` mapped through the same `classes_` table, not an independent argmax (so leaf majority and proba stay consistent). |
| BR-PROBA-4 | A fixture tree trained on only two of the three actions is a **required** test: the missing slot is 0, `decide` still returns an `Action`. |

## safety_mask (D24 + D50 item 5)

| ID | Rule |
| --- | --- |
| BR-MASK-1 | Fatal = `is_fatal(state, snake_id, action)` — deterministic deaths only. Head-to-head possibilities are not vetoed. |
| BR-MASK-2 | Mask **off**: `executed = proposed`, `vetoed = False`. |
| BR-MASK-3 | Mask **on** and `proposed` is non-fatal: `executed = proposed`, `vetoed = False`. |
| BR-MASK-4 | Mask **on** and `proposed` is fatal and at least one action is safe: `executed` is a safe action with maximal mapped proba. `vetoed = True`. |
| BR-MASK-5 | Tie on that maximum: if `straight` is among the tied safe actions, pick `straight` (no draw). Otherwise one `agent_generator` draw between the two turns. |
| BR-MASK-6 | Mask **on** and every action is fatal: `executed = proposed`, `vetoed = False` (the mask cannot help; RF05 does not claim a replacement). |
| BR-MASK-7 | The agent stream is built **lazily**, only on a left/right mask tie (D46 item 8). |

## Explanation (D50 item 6)

| ID | Rule |
| --- | --- |
| BR-XPL-1 | Every `decide` returns a `TreeExplanation` (never `None`). |
| BR-XPL-2 | `proba` has three floats in `_ACTIONS` order, after the `classes_` mapping. |
| BR-XPL-3 | `path` walks sklearn's `decision_path` from the root through every internal node to the leaf. Each `PathStep.went_left` equals `feature_value <= threshold`. |
| BR-XPL-4 | `vetoed` is exactly `executed is not proposed`. |
| BR-XPL-5 | U7 must be able to render the payload without importing sklearn or opening the `.joblib`. |

## Collection (Q3=A)

| ID | Rule |
| --- | --- |
| BR-COL-1 | Initial BC plays two pairings in **equal match counts**: expert vs expert and expert vs random. |
| BR-COL-2 | Labels are **expert actions only**. In expert vs expert both sides are kept. In expert vs random only the expert's snake is kept, **whichever side it occupies** (D52 item 4). |
| BR-COL-2b | Expert vs random **alternates NW/SE** by match index (D25 / D52 item 4). Each row stores `expert_side`. |
| BR-COL-3 | A row is `(extract_features(state, snake_id), expert.act(state, snake_id), match_id, seed, tick, snake_index, pairing, dagger_iter=0, expert_side)`. |
| BR-COL-4 | Collection continues until at least **100 000** labelled rows. Match seeds come from the collection stream in `core/rng.py`. |
| BR-COL-5 | Features are computed at the **pre-tick** state the expert saw — the same vector `TreeAgent` will see in play. |

## Split and freeze (D21)

| ID | Rule |
| --- | --- |
| BR-SPL-1 | Unique `match_id`s sorted ascending; first 80% → train, last 20% → test. |
| BR-SPL-2 | No `match_id` appears in both sides. |
| BR-SPL-3 | The test file is written once and **never appended to**. DAgger writes only into train. |
| BR-SPL-4 | The frozen test set is **not** used to choose `max_depth`, `min_samples_leaf`, `criterion`, or any other hyperparameter (D50 item 1). Depths 3/6/8 are product constants, not a search result. |

## Fit (D50 items 1 and 4)

| ID | Rule |
| --- | --- |
| BR-FIT-1 | Each product tree is `DecisionTreeClassifier(max_depth=d, min_samples_leaf=1, criterion="gini", class_weight="balanced", random_state=R)` for `d ∈ {3, 6, 8}`. |
| BR-FIT-2 | `R` is a documented integer stored in every sibling JSON. Two fits on the same `(X, y)` produce byte-identical trees (mandatory test). |
| BR-FIT-3 | The experimental depth/leaf/criterion grid, if run at all, lives in a report script and **must not** overwrite `models/bc_depth{3,6,8}.*`. |

## DAgger (D50 item 2)

| ID | Rule |
| --- | --- |
| BR-DAG-1 | Exactly **5** iterations, each refitting all three product depths on train ∪ new rows. |
| BR-DAG-2 | In an iteration **all three** current trees (mask off) play against the expert through `evaluation.batch`, **alternating sides** (D52 item 3). |
| BR-DAG-3 | New rows are the **three students'** pre-tick states, labelled by `ExpertAgent.act` on those states. They share one train set. `pairing="dagger"`, `dagger_iter=1..5`. Each iteration adds ~20% of the initial dataset (~20 000 rows on the full run). |
| BR-DAG-4 | After each iteration, record for every depth: accuracy on the **frozen** test set, and vs-random score rate (1/0.5/0) plus draw rate. |
| BR-DAG-5 | The per-iteration vs-random battery is **100** matches (curve). The U5 acceptance battery is **500** matches, run once on the final trees, mask off. |

## Acceptance and artefacts

| ID | Rule |
| --- | --- |
| BR-U5-ACC1 | Frozen-test accuracy ≥ 95% for BC-6 and BC-8. BC-3 has no accuracy floor; its number is still recorded. |
| BR-U5-ACC2 | Final BC-6 and BC-8 ≥ 90% vs `RandomAgent` over 500 matches (1/0.5/0); draw rate reported separately. |
| BR-U5-ACC3 | Inference mean of `extract_features` + `predict_proba` + `safety_mask` on kickoff, `obstacle_count=0`, is **< 1 ms**. Exceeding it is **ALERTA** in `benchmark.md`, never a pytest failure (D40). |
| BR-U5-ACC4 | D12 early check: 100 matches of BC-8 (mask **on**) and 100 of BC-6 (mask **off**) vs the expert; report the score-rate gap. **Alert only** — does not gate U5 (D27). |
| BR-U5-ART1 | Code Generation ships the pipeline and **tiny fixture** models under `models/fixtures/` for tests. |
| BR-U5-ART2 | The three real `models/bc_depth{3,6,8}.joblib` + JSON are produced by `scripts/train_bc.py` (off the default pytest). **U5 does not close without them** and they are committed at the end of U5 (D52 item 1). |

## Registry and layering

| ID | Rule |
| --- | --- |
| BR-REG-1 | `AgentSpec("tree", {"path": str, "safety_mask": bool})` builds via `TreeAgent.from_joblib` (D50 Q10=A). |
| BR-REG-2 | Unknown spec names still list `expert, human, random, tree`. |
| BR-LAY-1 | `agents.tree` imports `core` only (features, queries, rng). It does not import `training` or `evaluation`. |
| BR-LAY-2 | New streams are declared only in `core/rng.py`. |
