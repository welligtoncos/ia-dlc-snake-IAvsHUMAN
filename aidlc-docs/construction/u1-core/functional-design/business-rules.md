# U1 Core — Business Rules

Rules below are binding for `setup`, `engine`, and `queries`. Codes `BR-*` are for traceability into tests.

## Match lifecycle

| ID | Rule |
| --- | --- |
| BR-L1 | A match runs until one snake dies **or** `tick == max_ticks` (1800). Display rate is irrelevant. |
| BR-L2 | `step` on an already terminal `State` returns a **new equal snapshot** (pure); `tick` does not increase. |
| BR-L3 | `end_reason` is `None` while playing, `death` if at least one snake died this match, `timeout` if the tick cap was reached with both still alive. |
| BR-L4 | Timeout is **not** a `death_cause`. Both snakes keep `death_cause is None` on timeout. |
| BR-L5 | `outcome`: both dead this tick → `draw`; only A dead → `win_b`; only B dead → `win_a`; timeout → longer body wins, equal length → `draw`. |

## Spawns (D25)

| ID | Rule |
| --- | --- |
| BR-S1 | Each snake starts with 3 segments, facing the center. |
| BR-S2 | **NW**: head `(2,2)`, body `(1,2)`, `(0,2)`, facing `E`. **SE**: head `(17,17)`, body `(18,17)`, `(19,17)`, facing `W`. |
| BR-S3 | `sides` maps each `SnakeId` to `NW` or `SE`. Default (human vs machine): A=NW, B=SE. Tournaments flip by match index in U3/U7; U1 only honors the `sides` argument. |
| BR-S4 | Initial food: cyclic scan `(y, x)` starting at `(10, 9)`, wrap once; first cell not body and not obstacle (D26). Obstacles are placed **after** this food, so kickoff food is `(10, 9)` on an empty interior. |

## Obstacles (D26 / D29)

| ID | Rule |
| --- | --- |
| BR-O1 | `obstacle_count == 0` → empty set. Else `n` = count if even, else count+1. |
| BR-O2 | Forbidden (Chebyshev r=2): around each **head** and the cell **ahead** (NW `(3,2)`, SE `(16,17)`), plus initial bodies and the initial food cell. |
| BR-O3 | 180° symmetry: `(x,y)` implies `(width-1-x, height-1-y)`. Pairs placed together. |
| BR-O4 | Free cells for connectivity = in-bounds, not obstacle, **not initial body**. All free cells must be **one** 4-connected component. |
| BR-O5 | Failure → retry `seed_k = seed + k * 1000003`, `k = 0..99`. Then `SetupError`. |
| BR-O6 | Obstacle RNG stream is **not** the food-respawn stream (D31). Obstacles use `SeedSequence([seed_k, 0])`. No Python `hash()`. |
| BR-O7 | Obstacles are walls: entering one is `death_cause=obstacle`. They never move. |

## Food (D31)

| ID | Rule |
| --- | --- |
| BR-F1 | Kickoff food: D26 scan (no RNG). |
| BR-F2 | After a **surviving** eat, respawn by uniform choice among free cells (in-bounds, not body, not obstacle). List candidates in row-major `(y, x)` then `rng.choice`. |
| BR-F3 | Respawn RNG: `default_rng(SeedSequence([match_seed, tick]))` with `tick` = completed tick after this `step` (so `1..1800`). Stream key `0` is reserved for obstacles. |
| BR-F4 | Head-to-head on the food cell: resolve H2H first. Survivor eats and grows; if both die, **food stays**. |
| BR-F5 | Intent to eat (tail occupancy this tick) = `next_head == current_food`, even if the snake later dies. Actual consume = alive after deaths **and** intent. |
| BR-F6 | If the free set is empty, `food` becomes `None` (no exception). Eating is then impossible until a cell frees (not expected on 20×20 before timeout). |

## Movement and collisions

| ID | Rule |
| --- | --- |
| BR-M1 | Both snakes move in the same tick from the **same** pre-tick `State`. |
| BR-M2 | Actions are relative; reverse is not representable. |
| BR-M3 | **Wall**: next cell out of board → `wall`. |
| BR-M4 | **Obstacle**: next cell in `obstacles` → `obstacle`. |
| BR-M5 | **Tail vacate**: a tail cell is free this tick iff that snake does **not** intend to eat. Own tail uses the snake's **real** action (D29). |
| BR-M6 | **Own / opponent body**: `next` ∈ `next_occupancy` (D32) → `self_body` or `opponent_body`. Opponent's **pre-tick head** is body **unless** the move is a **swap**. Sem troca, aquela célula vira pescoço: `opponent_body`. |
| BR-M7 | **Head-to-head** only if (a) same `next` cell **or** (b) **swap** (`next_a == head_b` **and** `next_b == head_a`). Smaller dies `head_to_head`; equal length → both `head_to_head`. Entrar na cabeça do oponente **sem** troca **não** é H2H. |
| BR-M8 | H2H after wall/obstacle/body. If **exactly one** snake is still an H2H candidate, **that snake survives** (no size rule). The other already has its own `death_cause`. |
| BR-M9 | Both dead in the same tick → draw, regardless of causes (rule 8). Each `death_cause` is still stored (D31). |
| BR-M10 | Follow-the-vacating-tail is allowed (rule 9) except when that snake intends to eat. |

## Queries

| ID | Rule |
| --- | --- |
| BR-Q1 | `is_fatal` = wall, obstacle, or `next` ∈ `next_occupancy`. Opponent **current head is FATAL** (conservative: engine may spare the larger snake on a **swap** only). Same-`next` H2H on a third cell is **not** `is_fatal`. Docstring must state this (D32). |
| BR-Q2 | `next_occupancy(state, id, action, opponent_action=None)`: own tail removed iff this action does not land on food. Opponent tail: real eat if `opponent_action` set; else D29 (solid if opponent head 4-adjacent to food). Includes both current heads (D33). |
| BR-Q3 | Mandatory examples: (1) opponent head 4-adjacent to food → conservative tail solid; (2) A `(5,5)` E, B `(6,5)` N, both `straight` → A `opponent_body`, B lives (D32); (3) B adjacent to food, B turns and does not eat, A enters B's tail → A survives in `step` (D33). |
| BR-Q4 | `flood_fill_count(...) -> int` and `reachable_cells(...) -> frozenset[Cell]`. 4-connected, `limit=200`. Blocked: OOB, obstacles, and `occupancy` if given, else current bodies. Food is walkable. If `start` is blocked, count 0 / empty set. `limit < 1` raises `ValueError`. Internally a BFS over row-major integer indices with a precomputed blocked grid; `flood_fill_count` never materializes `Cell` objects (D43). |
| BR-Q5 | Setup connectivity uses the same 4-neighborhood but **ignores moving tails**; free = not obstacle and not initial body. |
| BR-Q6 | `engine.step` passo 5 **must** call `next_occupancy(..., opponent_action=real)`. `is_fatal` / U2 / U3 omit `opponent_action` (D33). |

## Purity and identity

| ID | Rule |
| --- | --- |
| BR-P1 | `step(state, a, b)` does not mutate `state`. |
| BR-P2 | `copy(s)` equals `s` field-wise; mutating the copy must not change `s`. |
| BR-P3 | Same `CoreConfig` + `seed` + `sides` → same `new_match` `State` (obstacles and kickoff food). |

## Acceptance tests (D30 / D31)

| ID | Rule |
| --- | --- |
| BR-A1 | Example tests cover rules 1–10 plus D32 ram-without-swap `(5,5)/(6,5)` and D33 tail-vacate when opponent adjacent to food but does not eat. |
| BR-A2 | 1000 matches with a **test helper** sampling each snake uniformly from the three actions; generator from the match seed (stream distinct from `0` and from `1..max_ticks`). No `RandomAgent` class in U1. Zero uncaught exceptions. |
| BR-A3 | Coverage ≥ 80% of `core/{state,setup,engine,queries}` at U1. After U2, ≥ 80% of all `core/` including `features.py`. |
| BR-A4 | PBT properties listed in `business-logic-model.md` (section Propriedades Testáveis). |

## Propriedades Testáveis (index)

Full statements live in `business-logic-model.md`. This file contributes business invariants BR-L*, BR-O*, BR-F*, BR-M* as PBT-03 inputs.
