# U5 Behavior Cloning — Domain Entities

Technology-agnostic except where a type is already fixed by U1–U3 (`Action`, `State`, `ActResult`). No Pygame. No clock inside `agents/` or `training/`.

## Package layout

```text
src/snake_vs_machine/
├── core/          # U1 + U2; rng.py gains the collection / DAgger tags
├── agents/
│   ├── tree.py    # TreeAgent, TreeExplanation, PathStep, ModelLoadError, safety_mask
│   └── registry.py  # gains "tree" (D50 Q10=A)
├── training/      # collect, dataset, fit, dagger
├── services/      # consumed, not modified
└── evaluation/    # scoring + batch consumed for vs-random curve
models/
├── fixtures/      # tiny trees for tests (U5 Code Generation)
└── bc_depth{3,6,8}.joblib + .json   # real artefacts, committed at U5 close (D52)
```

`training` depends on `core`, `agents`, `services` and `evaluation`. Nothing in `core` or `agents` imports `training`.

## TreeAgent (`agents/tree.py`)

| Field | Type | Meaning |
| --- | --- | --- |
| `_tree` | fitted `DecisionTreeClassifier` | Loaded from the `.joblib`; never refit in-process |
| `_meta` | `ModelMeta` | Versions and hyperparameters from the sibling JSON |
| `_safety_mask` | `bool` | Constructor flag (`from_joblib(path, safety_mask)`). Default off |

| Method | Signature | Meaning |
| --- | --- | --- |
| `from_joblib` | `from_joblib(path, safety_mask=False) -> TreeAgent` | Load `.joblib` + sibling `.json`; raise `ModelLoadError` on failure |
| `decide` | `decide(state, snake_id) -> ActResult` | Features → proposed action → optional mask → `ActResult` with `TreeExplanation` |
| `act` | `act(state, snake_id) -> Action` | `decide(...).action` |

Stateless about the last explanation (D45). One instance can play either snake.

### ModelMeta

Immutable record of the sibling JSON.

| Field | Type | Meaning |
| --- | --- | --- |
| `sklearn_version` | `str` | Exact pin written at train time (D50 item 8) |
| `numpy_version` | `str` | Must match the running `numpy==2.2.6` line |
| `feature_schema_version` | `int` | Must equal `FEATURE_SCHEMA_VERSION` (currently 1) |
| `feature_names` | `tuple[str, ...]` | Must equal `feature_names()` |
| `max_depth` | `int` | 3, 6 or 8 |
| `min_samples_leaf` | `int` | 1 (D50 item 1) |
| `criterion` | `str` | `"gini"` (D50 item 1) |
| `class_weight` | `str` | `"balanced"` |
| `random_state` | `int` | Fixed; two fits on the same matrix yield identical trees (D50 item 4) |

### ModelLoadError

Subclass of `Exception`. Library-side face of erro 4 (U4 owns the Portuguese text).

| Field | Type | Meaning |
| --- | --- | --- |
| `code` | `str` | Always `"model_load"` |
| `reason` | `str` | `missing` / `sklearn` / `numpy` / `schema` |

## TreeExplanation (concrete `ExplanationPayload`, D50 item 6)

Frozen `@dataclass(frozen=True, slots=True)` in `agents/tree.py`. Satisfies U3's empty `ExplanationPayload` Protocol structurally.

| Field | Type | Meaning |
| --- | --- | --- |
| `proposed` | `Action` | What the tree wanted (`predict`, before the mask) |
| `executed` | `Action` | What `MatchService` actually applies |
| `vetoed` | `bool` | `True` iff `executed is not proposed` |
| `proba` | `tuple[float, float, float]` | Mapped probabilities in `_ACTIONS` order (`straight`, `turn_left`, `turn_right`) |
| `path` | `tuple[PathStep, ...]` | Root → leaf, one step per internal node on the path |

U7 translates `feature_name` and renders `path` / `vetoed`. It does **not** load sklearn or walk `tree_`.

### PathStep

| Field | Type | Meaning |
| --- | --- | --- |
| `feature_name` | `str` | One of `feature_names()` |
| `threshold` | `float` | `tree_.threshold` at that node |
| `feature_value` | `float` | The value of that feature in **this** state's vector |
| `went_left` | `bool` | `True` when `feature_value <= threshold` (sklearn's left-child rule) |

The last step is the last internal node; the leaf is implied as the destination of `went_left`.

## Dataset (`.npz`, D50 item 3)

One file (or a pair `train.npz` / `test.npz` after the freeze). Arrays aligned on axis 0:

| Array | Dtype / shape | Meaning |
| --- | --- | --- |
| `X` | `float64 (n, 20)` | `extract_features` rows |
| `y` | `int8 (n,)` | Action index in `_ACTIONS` order (0/1/2) |
| `match_id` | `int64 (n,)` | Groups ticks of one `play` |
| `seed` | `int64 (n,)` | Match seed |
| `tick` | `int32 (n,)` | `state.tick` at the labelled decision |
| `snake_index` | `int8 (n,)` | 0 for A, 1 for B (never `SnakeId.auto()`) |
| `pairing` | `U16 (n,)` | `expert_vs_expert` / `expert_vs_random` / `dagger` |
| `dagger_iter` | `int8 (n,)` | `0` for the initial BC; `1..5` for DAgger |
| `expert_side` | `int8 (n,)` | `0` = NW, `1` = SE — spawn side of the labelled expert (D52 item 4) |

File metadata (npz `allow_pickle` object or a sibling key): `FEATURE_SCHEMA_VERSION`, numpy version string, `feature_names`.

### Split

80/20 **by `match_id`**, not by row. Unique `match_id`s sorted ascending; the first 80% are train, the last 20% are test. No extra RNG, no Python `hash()`. The test membership is frozen before the first DAgger iteration and never grows (D21).

## Training run record

Written next to the three models (and appended after each DAgger iteration).

| Field | Meaning |
| --- | --- |
| `iteration` | `0` = initial BC, `1..5` = after that DAgger pass |
| `accuracy_frozen` | Per depth, on the frozen test set |
| `score_vs_random` | Per depth, 1/0.5/0 (draw rate separate) |

## AgentSpec extension

`AgentSpec("tree", {"path": "<joblib path>", "safety_mask": true|false})`. `build_agent` calls `TreeAgent.from_joblib`. The worker reads the file from disk after `spawn` (D48 item 1).

## New RNG streams (`core/rng.py` only)

| Stream | Composition | Owner |
| --- | --- | --- |
| Collection matches | `[batch_seed, 4_000_003, pairing_code, match_index]` | `training.collect` |
| DAgger matches | `[batch_seed, 5_000_003, dagger_iter, match_index]` | `training.dagger` |

`pairing_code` is `0` for expert vs expert and `1` for expert vs random. Agent draws inside a match stay on `[seed, 3_000_003, tick, snake_index]`. sklearn uses the integer `random_state` from `ModelMeta`, not a `SeedSequence`.

## Out of this unit

Portuguese erro 4 copy (U4); translating `TreeExplanation` (U7); 500-match D12 / 40% vs expert / noise (U7); `TimedAgent` (U7); VIPER (U6).
