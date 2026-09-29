# U2 Features — Business Rules

Codes `BR-FTR-*` are for tests. Occupancy in this unit is always **conservative** (`opponent_action` omitted, D33).

## Preconditions

| ID | Rule |
| --- | --- |
| BR-FTR-P1 | `extract_features` is pure: does not mutate `state`. |
| BR-FTR-P2 | Same `(state, snake_id)` → same `FeatureVector`. |
| BR-FTR-P3 | If `not state.snake(id).alive` **or** `state.end_reason is not None`, raise `ValueError`. Do not return a vector (D38). |
| BR-FTR-P4 | PBT generators keep only non-terminal states with both snakes alive (D38). |

## Schema

| ID | Rule |
| --- | --- |
| BR-FTR-S1 | Vector length 20 in the `feature_names()` order (domain-entities table). |
| BR-FTR-S2 | `FEATURE_SCHEMA_VERSION` is an `int` (initial `1`) next to `feature_names()`. U5 writes it on each model JSON. U5 `TreeAgent` refuses a different version (erro 4). |
| BR-FTR-S3 | Binaries ∈ `{0, 1}`; `dist_*` and `space_free_*` ∈ `[0, 1]`; `length_diff` is an integer. |

## Danger and rays

| ID | Rule |
| --- | --- |
| BR-FTR-D1 | `danger_d = 1` iff `is_fatal(state, snake_id, action_d)` (Q1=A). Computed as `_blocked(state, landing_d, occ_d)`, the same three conditions, reusing `occ_d` instead of rebuilding it inside `is_fatal` (D43). PBT P-FEAT-DANGER guards the equivalence. |
| BR-FTR-D2 | `dist_danger_d`: start at the **landing** cell of `action_d`. Blocked = out of board, obstacle, or ∈ `next_occupancy(state, id, action_d)` (conservative). Do **not** use raw current bodies (Q2=X). |
| BR-FTR-D3 | If the landing cell is blocked → `dist_danger_d = 0`. Else count landing plus further **free** cells along that ray until (not including) the first blocked cell. `value = count / max(width, height)`, clip `[0, 1]`. |
| BR-FTR-D4 | `danger_d = 1 ⇔ dist_danger_d = 0` (D38). |
| BR-FTR-D5 | Food is not a blocker on the ray. |

## Space free (D25)

| ID | Rule |
| --- | --- |
| BR-FTR-SP1 | If `is_fatal` for that action → `space_free_d = 0` (Q3=A). |
| BR-FTR-SP2 | Else `flood_fill_count(...) / min(200, free_cells)`, clip `[0, 1]`. **Only** `flood_fill_count` (D39). Do not derive space from `reachable_cells` when `limit` binds. |
| BR-FTR-SP2b | `flood_fill_count` = exactly `min(reachable_component_size, limit)`, independent of BFS visit order. U1 test: count unchanged after whole-board rotate/mirror on constructed states (D39). |
| BR-FTR-SP3 | `free_cells` = in-bounds cells that are not **current** bodies and not obstacles. Food counts as free. Same denominator for all three directions (Q4=A). Computed once per call as `width*height - len(obstacles) - len(me.body) - len(opp.body)` (D42). |
| BR-FTR-SP4 | If `free_cells <= 0`, `space_free_d = 0` (no division by zero). |
| BR-FTR-SP5 | `danger_d = 1 ⇒ space_free_d = 0` (D38). |

## Food and distances

| ID | Rule |
| --- | --- |
| BR-FTR-FO1 | If `food is None` or food equals the requested head → `food_*` all `0`; `dist_food = 1`; `opponent_closer_to_food = 0` (Q5/Q6). |
| BR-FTR-FO2 | Otherwise inclusive semi-planes in the head frame: `ahead = (dot(food-head, forward) > 0)`, same for left/right/behind. A diagonal may set **two** bits. A pure axis sets one bit (Q5=B). |
| BR-FTR-FO3 | `dist_food = manhattan(head, food) / (width + height - 2)`, clip `[0, 1]` (Q6=A). |
| BR-FTR-FO4 | `dist_opponent_head = manhattan(my_head, opp_head) / (width + height - 2)`, clip `[0, 1]`. |
| BR-FTR-FO5 | `opponent_closer_to_food = 1` iff `manhattan(opp, food) < manhattan(me, food)` (strict). Tie → `0`. |

## Head risk and length

| ID | Rule |
| --- | --- |
| BR-FTR-HR1 | `head_risk_d = 1` iff the landing cell of `action_d` equals any of the opponent's **three** possible next heads (`straight`, `turn_left`, `turn_right`). Discard opponent next cells that are out of board (Q7=B). |
| BR-FTR-HR2 | If my landing is out of board, `head_risk_d = 0` (it cannot equal an in-bounds next head). |
| BR-FTR-LD1 | `length_diff = me.length - opp.length`. |

## Geometry PBT (D19 + D38)

| ID | Rule |
| --- | --- |
| BR-FTR-G1 | Rotate the **whole board** 90/180/270° about the center (square board): same `FeatureVector` for the same `snake_id`. |
| BR-FTR-G2 | Mirror the **whole board** `x → W-1-x` **or** `y → H-1-y`: left ↔ right slots swap; ahead/behind and non-lateral slots unchanged. |
| BR-FTR-G3 | Transforms rewrite both bodies, both directions, food, and obstacles. Not around the head. |
| BR-FTR-G4 | States for PBT come from `new_match` + `step` (D36), then the transform. Example tests may `_place`. |

## Acceptance (D30 / D38)

| ID | Rule |
| --- | --- |
| BR-FTR-A1 | Example tests: D39 golden vector + fairness; danger/ray/space_free/food/head_risk/ValueError (worked examples 4–8). |
| BR-FTR-A2 | After U2 CG, coverage ≥ 80% branch of all `core/` including `features.py` (remove `omit`). |
| BR-FTR-A3 | PBT properties in `business-logic-model.md`. |

## Propriedades Testáveis (index)

Full statements live in `business-logic-model.md`.
