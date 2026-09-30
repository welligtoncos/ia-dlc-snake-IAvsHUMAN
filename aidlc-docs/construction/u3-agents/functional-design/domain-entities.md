# U3 Agents + MatchService — Domain Entities

Technology-agnostic. No Pygame, no sklearn, no clock. All U1 types are reused unchanged.

## Package layout (D44 item 6)

`services/` is a **new** package, outside the original D28 list:

```text
src/snake_vs_machine/
├── core/        # U1 + U2 (unchanged here)
├── agents/      # U3: base, random_agent, expert, human
├── services/    # U3: match  <- new package (D44)
├── training/    # U5
├── evaluation/  # U7 (TimedAgent lives here, D44 item 5)
└── ui/          # U4
```

`services` depends on `core` and `agents`; it is consumed by `ui`, `training` and `evaluation`. Nothing in `core` or `agents` imports `services`.

## Agent (protocol, Q12=A)

Structural contract in `agents/base.py` — `typing.Protocol`, no inheritance required, trivially faked in tests.

| Member | Signature | Meaning |
| --- | --- | --- |
| `act` | `act(state: State, snake_id: SnakeId) -> Action` | The action this agent plays for `snake_id` on `state` |

The side is a **parameter**, not constructor state (Q1=B). One agent instance can therefore play either snake, and tournament side alternation needs no agent rebuild. **Every** agent in the project implements `act`, including the U5 `TreeAgent`.

`RandomAgent` and `ExpertAgent` are pure functions of `(state, snake_id)`; `HumanAgent` is the only stateful agent (D44 item 3).

## ExplainingAgent (optional protocol, D45 item 1)

Second `Protocol` in `agents/base.py`, implemented **only** by the U5 `TreeAgent`. U3 declares it so `MatchService` can route explanations without importing U5.

| Member | Signature | Meaning |
| --- | --- | --- |
| `decide` | `decide(state: State, snake_id: SnakeId) -> ActResult` | The executed action plus its explanation |

An `ExplainingAgent` also satisfies `Agent`: its `act` returns `decide(...).action`.

### ActResult

Immutable `@dataclass(frozen=True, slots=True)` in `agents/base.py`.

| Field | Type | Meaning |
| --- | --- | --- |
| `action` | `Action` | The action actually executed (after the U5 safety mask, when there is one) |
| `explanation` | `ExplanationPayload \| None` | Explanation data; `None` for agents that do not explain |

### ExplanationPayload

Declared in `agents/base.py` as an **empty structural `Protocol`** — a marker U3 can reference without inventing U5's contents. U5 defines the concrete payload (decision path conditions, proposed action, executed action, veto flag — D30). `MatchService` and `on_tick` treat it as opaque.

**No agent stores its last explanation** (D45 item 1). The payload exists only as the return value of `decide`, flowing to U7 through `on_tick`. There is therefore no `explain(state)` method and no `last_explanation` attribute anywhere.

## RandomAgent (`agents/random_agent.py`)

| Field | Type | Meaning |
| --- | --- | --- |
| — | — | Stateless; no constructor arguments |

Uniform draw over the non-fatal actions, falling back to all three when every action is fatal (Q2=B). Randomness comes from the tick stream, not from instance state.

## ExpertAgent (`agents/expert.py`)

| Field | Type | Meaning |
| --- | --- | --- |
| — | — | Stateless; no constructor arguments |

Internal value object, private to the module, so the rotation property can detect draws:

### ActionEvaluation (internal)

| Field | Type | Meaning |
| --- | --- | --- |
| `action` | `Action` | The relative action being scored |
| `landing` | `Cell` | Next head cell |
| `occupancy` | `frozenset[Cell]` | Conservative `next_occupancy` for this action (D33) |
| `fatal` | `bool` | Out of board, obstacle, or landing in `occupancy` |
| `head_risk` | `bool` | Landing ∈ opponent's in-bounds possible next heads |
| `flood` | `int` | `flood_fill_count(landing, occupancy, limit=200)` |
| `food_distance` | `int \| None` | BFS steps from `landing` to the food; `None` if unreachable or no food |

### ExpertDecision (internal)

| Field | Type | Meaning |
| --- | --- | --- |
| `action` | `Action` | Chosen action |
| `stage` | `str` | Which rule decided: `ranked`, `fallback_space`, `fallback_head_risk`, `all_fatal` |
| `drawn` | `bool` | True when a left/right tie was resolved by RNG (D44 item 2 exception) |

`act` returns `decision.action`; tests use the private `_decide` to read `drawn`.

## HumanAgent (`agents/human.py`)

| Field | Type | Meaning |
| --- | --- | --- |
| `_buffer` | `deque[Direction]` (maxlen 2) | Pending absolute commands, FIFO; when full, a **new** command is ignored (D45 item 2) |
| `_last_direction` | `Direction \| None` | Direction observed at the last `act`; seeds the "effective direction" before the first tick |

| Method | Signature | Meaning |
| --- | --- | --- |
| `push_absolute` | `push_absolute(direction: Direction) -> None` | Enqueue an absolute command; reverse and redundant commands are dropped here (D44 item 4) |
| `act` | `act(state, snake_id) -> Action` | Consume at most one command and convert it to a relative action |

Absolute keys are `Direction` values. Key codes belong to U4 — the UI translates a keypress into a `Direction` before calling `push_absolute`.

## MatchResult (`services/match.py`, Q8=C)

Immutable `@dataclass(frozen=True, slots=True)`.

| Field | Type | Meaning |
| --- | --- | --- |
| `outcome` | `Outcome` | `win_a`, `win_b` or `draw` (from `engine.outcome`) |
| `end_reason` | `EndReason` | `death` or `timeout` |
| `ticks` | `int` | Ticks played (final `state.tick`) |
| `length_a` / `length_b` | `int` | Final lengths |
| `death_cause_a` / `death_cause_b` | `DeathCause \| None` | `None` when the snake is alive (timeout) |
| `seed` | `int` | Match seed, so any result is reproducible |
| `side_a` / `side_b` | `Side` | Spawn assignment actually used |

**No `score_a`** (D48 item 5, revising the D44/Q8 list): the 1 / 0.5 / 0 mapping has a single home in `evaluation/scoring.py`, and `services` must not import `evaluation`. `outcome` already determines the score, so storing it here would duplicate the rule. No trajectory is stored either: U5 collects one through the `on_tick` hook (Q8=C).

## TickHook (callback type)

`Callable[[State, ActResult, ActResult, State], None]` — state before the tick, the result of each agent, state after. Called once per tick when `play` receives it. Purely observational: `play` ignores the return value.

Carrying `ActResult` instead of a bare `Action` is what lets U7 render explanations and U5 collect trajectories through the same hook (D45 item 1). For agents that only implement `act`, `MatchService` wraps the action as `ActResult(action, None)`.

## Relationships

```text
Agent (protocol)
  ├── RandomAgent   -> core.queries.is_fatal
  ├── ExpertAgent   -> core.queries.{is_fatal, next_occupancy, flood_fill_count} + private BFS
  ├── HumanAgent    -> core.state only
  └── TreeAgent (U5, also ExplainingAgent) -> core.features + sklearn + safety_mask

services.match.tick(state, agent_a, agent_b) -> core.engine.step
services.match.play(...)  -> core.setup.new_match + tick loop -> MatchResult
```

## Out of this unit

`agents.tree` and `safety_mask` (U5) — U3 only declares the `ExplainingAgent` / `ActResult` / `ExplanationPayload` contracts they will satisfy; `TimedAgent` and tournaments (U7); key handling and pacing (U4); trajectory persistence (U5).
