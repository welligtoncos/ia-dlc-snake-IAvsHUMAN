# U3 Agents + MatchService — Business Rules

`_ACTIONS` is the fixed order `(straight, turn_left, turn_right)` everywhere in this unit.
`snake_index` is **0 for `SnakeId.A`, 1 for `SnakeId.B`** — written explicitly, never taken from the enum's `auto()` value.

## Agent contract

| ID | Rule |
| --- | --- |
| BR-AGT-1 | `Agent` is a `typing.Protocol` with `act(state: State, snake_id: SnakeId) -> Action` (Q12=A). The side is a parameter, so one instance can play either snake (Q1=B). |
| BR-AGT-2 | `act` returns one of the three relative actions. It never returns `None` and never raises for a playing state. |
| BR-AGT-3 | `act` must not mutate `state` — U1 types are frozen, so this is structural. |
| BR-AGT-4 | `RandomAgent.act` and `ExpertAgent.act` are pure functions of `(state, snake_id)`: same inputs → same action, no instance state (D44 item 3). `HumanAgent` is the only stateful agent. |
| BR-AGT-5 | Calling `act` on a terminal state or a dead snake raises `ValueError`, matching `extract_features` (D38). `MatchService` never does it. |
| BR-AGT-6 | `ExplainingAgent` is a second, optional `Protocol` with `decide(state, snake_id) -> ActResult`, implemented only by the U5 `TreeAgent` (D45 item 1). It also satisfies `Agent`: `act` returns `decide(...).action`. |
| BR-AGT-7 | No agent stores its last explanation. The payload only travels as the return value of `decide` — no `explain(state)` method, no `last_explanation` attribute (D45 item 1). |
| BR-AGT-8 | `ExplanationPayload` is an empty structural `Protocol` in U3; U5 supplies the concrete type. `MatchService` never inspects it. |

## Randomness (D44 item 3)

| ID | Rule |
| --- | --- |
| BR-RNG-1 | Any agent randomness comes from `numpy.random.default_rng(SeedSequence([state.seed, 3_000_003, state.tick, snake_index]))`. No Python `hash()`, no global RNG, no clock. |
| BR-RNG-2 | The tag `3_000_003` separates this stream from U1's obstacle stream (`[seed_k, 0]`), food respawn stream (`[seed, tick_after]`) and the U1 test helper (`[seed, 2_000_003]`). |
| BR-RNG-3 | Because the stream is derived from the state, a replay of the same `(seed, tick)` reproduces the same draw — the agent stays a pure function. |
| BR-RNG-4 | The `SeedSequence` and `Generator` are built **lazily**, only when a draw is actually needed (D46 item 8). Construction costs 31.3 µs, so the expert — which draws only on a left/right tie — pays nothing on the common path. |

## RandomAgent (Q2=B)

| ID | Rule |
| --- | --- |
| BR-RND-1 | Candidates = actions with `is_fatal(state, snake_id, action)` false, evaluated in `_ACTIONS` order. |
| BR-RND-2 | If at least one candidate exists, draw uniformly among candidates. |
| BR-RND-3 | If every action is fatal, draw uniformly among all three (death is unavoidable; the agent still plays). |
| BR-RND-4 | The draw is `candidates[int(rng.integers(len(candidates)))]` — index-based, so the result depends only on the candidate order and the stream. |

## ExpertAgent (D44 item 1)

### Per-action evaluation

| ID | Rule |
| --- | --- |
| BR-EXP-1 | For each action: `landing, facing = next_head(head, direction, action)`; `occ = next_occupancy(state, snake_id, action)` — conservative, **without** `opponent_action` (D33). |
| BR-EXP-2 | `fatal` = landing out of board, or in `state.obstacles`, or in `occ` (identical to `is_fatal`; same three conditions as U2's `_blocked`, D43). |
| BR-EXP-3 | `head_risk` = landing is in bounds and belongs to the opponent's in-bounds possible next heads (the same set U2 uses for `head_risk_*`). |
| BR-EXP-4 | `flood` = `flood_fill_count(state, landing, occupancy=occ, limit=200)`. |
| BR-EXP-5 | `food_distance` = number of BFS steps between `landing` and `state.food`, over blocked = `occ ∪ state.obstacles`; `0` when `landing` is the food; `None` when the food is unreachable or `state.food is None`. The BFS spans the whole board — it is a distance, so no 200 cap (Q4=X). |
| BR-EXP-5b | Computed by **one** BFS from the **food** per call, not three from the landings (D46 item 3). Blocked set = `state.obstacles ∪ next_occupancy` for a non-eating action (own tail released). Each action then reads `distance[landing]`, and an action landing on the food is `0` by BR-EXP-5. This is exact, not an approximation — see the note in `business-logic-model.md`. |
| BR-EXP-6 | The opponent's possible next heads block **only** the landing cell, through `head_risk`. They are **not** blocked inside the `food_distance` BFS, because heads two or more steps ahead are unknowable (Q4=X). |

### Decision order

| ID | Rule |
| --- | --- |
| BR-EXP-7 | `S1` = the three actions minus the fatal ones. |
| BR-EXP-8 | `S2` = `S1` minus the `head_risk` ones — **skipped entirely** (`S2 = S1`) when the expert is strictly longer than the opponent (`me.length > opp.length`), since the larger snake survives a head swap. |
| BR-EXP-9 | `S3` = `S2` minus the actions that fail `flood > me.length` (Q5=A: strict `>`, current body length, growth ignored). |
| BR-EXP-10 | If `S3` is non-empty, rank it by: smallest `food_distance` (`None` sorts last, after every finite distance) → largest `flood` → `straight` preferred over turns. |
| BR-EXP-11 | If the winner after BR-EXP-10 is a tie **between `turn_left` and `turn_right`**, resolve it by one draw from the tick RNG (BR-RNG-1). Mark the decision `drawn = True`. |
| BR-EXP-12 | Fallback: if `S3` is empty, decide on `S2` by largest `flood` (then `straight`, then the left/right draw). If `S2` is empty, decide on `S1` the same way. |
| BR-EXP-13 | Fallback: if `S1` is empty (every action is fatal), return `straight`. No draw, no flood comparison. |
| BR-EXP-14 | The order is total: for a fixed `(state, snake_id)` the expert is deterministic, including the draw, which depends only on `(seed, tick, snake_index)`. |

## HumanAgent (RF01, D13, D44 item 4)

| ID | Rule |
| --- | --- |
| BR-HUM-1 | Buffer is FIFO with capacity **2**. Pushing onto a **full** buffer **ignores the new command** (D45 item 2, overriding the "evict oldest" wording of D28). Each buffered command was validated against its predecessor, so evicting the head would leave a command validated against a direction that never happens — which can turn into a reverse. |
| BR-HUM-2 | The **effective direction** at push time is the last command already in the buffer, or `_last_direction` when the buffer is empty. |
| BR-HUM-3 | `push_absolute` drops a command that equals the effective direction (redundant — it would resolve to `straight` anyway). |
| BR-HUM-4 | `push_absolute` drops a command that is the reverse of the effective direction (D13). Filtering happens at push, never at `act` (Q7=X). |
| BR-HUM-5 | When `_last_direction` is `None` (no tick observed yet) and the buffer is empty, the command is accepted as-is. |
| BR-HUM-6 | `act` first records `_last_direction = state.snake(snake_id).direction`. |
| BR-HUM-7 | `act` on an empty buffer returns `straight` and consumes nothing. |
| BR-HUM-8 | `act` on a non-empty buffer pops exactly **one** command (the oldest) and converts it: equal to the current direction → `straight`; left neighbour → `turn_left`; right neighbour → `turn_right`. |
| BR-HUM-9 | A popped command that reverses the current direction returns `straight` — defensive only; BR-HUM-4 prevents it from ever entering the buffer. |
| BR-HUM-10 | Exactly one command leaves the buffer per tick. Chained turns therefore take two ticks, which is what the buffer of 2 is for. |
| BR-HUM-11 | Mandatory example (D45 item 2): snake facing **east**, then `↑ ← ↓` pressed faster than the tick. Buffer ends as `[↑, ←]` — `↑` accepted against `E`, `←` accepted against `↑`, `↓` ignored because the buffer is full. Evicting the oldest instead would leave `[←, ↓]`, and popping `←` while still facing east is a **reverse**. |

## MatchService (`services/match.py`, Q11=A)

| ID | Rule |
| --- | --- |
| BR-MS-1 | `tick(state, agent_a, agent_b) -> State` asks each agent for its result, then calls `engine.step(state, result_a.action, result_b.action)`. Both agents see the **same** pre-tick state (simultaneous movement, D14). |
| BR-MS-1b | Per agent: if it implements `decide` (runtime-checkable `ExplainingAgent`), `MatchService` calls `decide` and keeps the `ActResult`; otherwise it calls `act` and wraps the action as `ActResult(action, None)` (D45 item 1). `decide` is never called twice for one tick. |
| BR-MS-2 | `tick` has no clock: no `sleep`, no `time` read, no frame rate. Pacing belongs to the caller (D28). |
| BR-MS-3 | `tick` on a terminal state raises `ValueError`. |
| BR-MS-4 | `play(agent_a, agent_b, config, seed, sides=(Side.NW, Side.SE), on_tick=None) -> MatchResult` builds the state with `new_match(config, seed, sides)` and ticks until `engine.is_terminal`. |
| BR-MS-5 | Side assignment comes from the caller (Q9=A). `play` never computes match-index parity; tournaments in U7 do that and pass `sides`. |
| BR-MS-6 | `on_tick`, when given, is called once per tick with `(state_before, result_a, result_b, state_after)`, where each result is the `ActResult` produced above — so explanations reach U7 through the hook (D45 item 1). `play` stores no trajectory itself (Q8=C). |
| BR-MS-7 | `MatchResult` exposes `outcome`, not a score. The 1 / 0.5 / 0 mapping (D14b) and the win / draw rates live in `evaluation/scoring.py` (D48 item 5); the draw rate is always reported separately from the win rate. |
| BR-MS-8 | `play` terminates in at most `config.max_ticks` ticks, because `engine.step` sets `end_reason = timeout` there (D14). |
| BR-MS-9 | `MatchResult` carries only finished-match facts (see `domain-entities.md`); it holds no `State`, so it stays cheap for 500-match batteries. |

## Acceptance and measurement (Q10=A)

| ID | Rule |
| --- | --- |
| BR-U3-ACC1 | Expert ≥ 95% score (1 / 0.5 / 0) vs `RandomAgent` over **500** matches, plus the draw rate reported separately. Run as a script; result recorded in `aidlc-docs/construction/u3-agents/benchmark.md`. |
| BR-U3-ACC2 | pytest keeps a fast reduced version of BR-U3-ACC1 (small N) in the normal run; the full 500-match battery is marked `slow` and excluded by default. |
| BR-U3-ACC3 | RNF03: ≥ 1000 matches/min random vs random, measured by the same script and recorded in `benchmark.md`. Throughput vs the expert is measured and recorded with **no floor** (D17). |
| BR-U3-ACC4 | Inference latency is **not** measured in U3. A `TimedAgent` wrapper in `evaluation` (U7) does it, so `MatchService` stays clockless (D44 item 5). |
