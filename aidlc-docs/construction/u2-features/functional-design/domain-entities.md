# U2 Features — Domain Entities

Technology-agnostic types for `core.features`. Identifiers in English. Reuses U1 `State`, `SnakeId`, `Action`, `Cell`, `Direction`.

## Public surface

| Symbol | Kind | Meaning |
| --- | --- | --- |
| `extract_features(state, snake_id)` | function | Pure; returns `FeatureVector` or raises `ValueError` (D38) |
| `feature_names()` | function | Fixed `tuple` of 20 English names, sklearn column order |
| `FEATURE_SCHEMA_VERSION` | `int` | Starts at `1`. Bump when layout or semantics change. U5 persists this on each model JSON; `TreeAgent` refuses a mismatch (erro 4) |

No sklearn, pygame, or I/O in this unit.

## FeatureVector

Immutable `tuple` of length 20 (Q8=A). Slots 0–18 are `0`/`1` or a real in `[0, 1]`. Slot 19 (`length_diff`) is an `int` (may be stored as that `int` inside the tuple). Callers that need an array use `numpy.asarray`.

| Index | Name | Domain |
| --- | --- | --- |
| 0 | `danger_ahead` | `{0, 1}` |
| 1 | `danger_left` | `{0, 1}` |
| 2 | `danger_right` | `{0, 1}` |
| 3 | `dist_danger_ahead` | `[0, 1]` |
| 4 | `dist_danger_left` | `[0, 1]` |
| 5 | `dist_danger_right` | `[0, 1]` |
| 6 | `space_free_ahead` | `[0, 1]` |
| 7 | `space_free_left` | `[0, 1]` |
| 8 | `space_free_right` | `[0, 1]` |
| 9 | `food_ahead` | `{0, 1}` |
| 10 | `food_left` | `{0, 1}` |
| 11 | `food_right` | `{0, 1}` |
| 12 | `food_behind` | `{0, 1}` |
| 13 | `dist_food` | `[0, 1]` |
| 14 | `opponent_closer_to_food` | `{0, 1}` |
| 15 | `dist_opponent_head` | `[0, 1]` |
| 16 | `head_risk_ahead` | `{0, 1}` |
| 17 | `head_risk_left` | `{0, 1}` |
| 18 | `head_risk_right` | `{0, 1}` |
| 19 | `length_diff` | `int` (`my_length - opponent_length`) |

`feature_names()` returns exactly these names in this order.

## Relative directions

Ahead / left / right map to `Action.straight` / `turn_left` / `turn_right` from the requested snake's current facing (U1 `next_head`).

## Head-frame basis (y grows down)

| Facing | Forward `(dx, dy)` | Left | Right |
| --- | --- | --- | --- |
| `E` | `(+1, 0)` | `(0, -1)` | `(0, +1)` |
| `W` | `(-1, 0)` | `(0, +1)` | `(0, -1)` |
| `N` | `(0, -1)` | `(-1, 0)` | `(+1, 0)` |
| `S` | `(0, +1)` | `(+1, 0)` | `(-1, 0)` |

Behind = `-forward`.

## Board transforms (D38 / D19)

Used only in tests. Production `extract_features` does not rotate the board.

Square board required for rotation (`width == height`; default 20).

| Transform | Cell | Direction |
| --- | --- | --- |
| Rot 90° CW about center | `(x, y) → (W-1-y, x)` | `N→E→S→W→N` |
| Rot 180° | `(x, y) → (W-1-x, H-1-y)` | `N↔S`, `E↔W` |
| Rot 270° CW | `(x, y) → (y, H-1-x)` | inverse of 90° CW |
| Mirror vertical axis | `(x, y) → (W-1-x, y)` | `E↔W` |
| Mirror horizontal axis | `(x, y) → (x, H-1-y)` | `N↔S` |

Apply to **both** bodies, both facings, food (if any), and every obstacle.

## Errors

| Type | When |
| --- | --- |
| `ValueError` | Requested snake is not `alive`, **or** `state.end_reason is not None` (D38) |

## Out of U2

`TreeAgent` load check, PT labels (U7), `safety_mask`, agents, MatchService.
