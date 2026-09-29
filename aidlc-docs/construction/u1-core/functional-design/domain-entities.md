# U1 Core — Domain Entities

Technology-agnostic types for `core.state`, `core.setup`, `core.engine`, `core.queries`. Identifiers in English.

## Enumerations

| Type | Values | Notes |
| --- | --- | --- |
| `SnakeId` | `A`, `B` | Two snakes; `step` takes `action_a` and `action_b` |
| `Side` | `NW`, `SE` | Spawn template (D25) |
| `Direction` | `N`, `E`, `S`, `W` | Absolute on the grid |
| `Action` | `straight`, `turn_left`, `turn_right` | Relative to current facing; reverse is not a value |
| `DeathCause` | `wall`, `obstacle`, `self_body`, `opponent_body`, `head_to_head` | Per snake; `None` while alive. **Not** timeout (D31) |
| `EndReason` | `death`, `timeout` | Match-level; `None` while playing (D31) |
| `Outcome` | `win_a`, `win_b`, `draw` | Only meaningful when terminal |

## Geometry

### Cell
`NamedTuple` with `x: int`, `y: int` (D34). Origin `(0, 0)` is **top-left**; `x` grows right; `y` grows down. Legal cells: `0 <= x < width`, `0 <= y < height` (default 20).

### Direction deltas

| Direction | Delta `(dx, dy)` |
| --- | --- |
| `E` | `(+1, 0)` |
| `W` | `(-1, 0)` |
| `N` | `(0, -1)` |
| `S` | `(0, +1)` |

Relative turns (screen left/right with `y` down):

| Facing | `turn_left` | `turn_right` |
| --- | --- | --- |
| `N` | `W` | `E` |
| `E` | `N` | `S` |
| `S` | `E` | `W` |
| `W` | `S` | `N` |

`straight` keeps the facing.

## Snake

`@dataclass(frozen=True, slots=True)` (D34).

| Field | Type | Meaning |
| --- | --- | --- |
| `id` | `SnakeId` | Identity |
| `body` | `tuple[Cell, ...]` | Index 0 = head, last = tail. Length ≥ 3 while alive |
| `direction` | `Direction` | Facing of the head |
| `alive` | `bool` | `True` until a death this match |
| `death_cause` | `DeathCause \| None` | Per D31 |

`length` = `len(body)`. While alive, cells in `body` are unique. After every `step`, the union of cells of **living** snakes has no duplicates (**P-ENG-NOOVERLAP**, D32).

## CoreConfig

`@dataclass(frozen=True, slots=True)` (D34/D35). All fields are `int`. No mutable collections.

| Field | Default | Role |
| --- | --- | --- |
| `width` | 20 | Board |
| `height` | 20 | Board |
| `max_ticks` | 1800 | Logical cap; independent of display `tick_rate` |
| `obstacle_count` | 0 | Requested count; engine uses even `n` (D26) |

`tick_rate` is **not** a core field.

## State

`@dataclass(frozen=True, slots=True)` (D34). `copy(state)` is structural equality / `dataclasses.replace` (values are already immutable; P-COPY).

| Field | Type | Meaning |
| --- | --- | --- |
| `width`, `height` | `int` | Board size |
| `max_ticks` | `int` | 1800 unless tests override |
| `tick` | `int` | Completed ticks; `0` at kickoff |
| `seed` | `int` | Match seed |
| `snake_a`, `snake_b` | `Snake` | Fixed fields only (D35). Accessor `snake(id)` — **no** `dict` map |
| `food` | `Cell \| None` | None only if no free cell after eat |
| `obstacles` | `frozenset[Cell]` | Internal walls |
| `end_reason` | `EndReason \| None` | Playing / death / timeout |
| `side_a`, `side_b` | `Side` | Fixed fields only (D35) — **no** `dict` map |

Invariants while `end_reason is None`: both `alive`; `tick < max_ticks`; `food` is a cell not overlapping bodies or obstacles (unless `None` on a full board).

**D35**: `State`, `Snake`, and `CoreConfig` contain only hashable immutable fields. `hash(state)` is defined. Assigning any field raises `FrozenInstanceError`. `new_match(..., sides=)` may accept a mapping **at the call boundary** and immediately store `side_a`/`side_b` — the mapping is not kept on `State`.

## Errors

| Type | When |
| --- | --- |
| `SetupError` | Obstacle generation failed connectivity/zones after 100 retries |

No clock, no Pygame, no agent types in these entities.

## Relationships

```
+-----------------------------------------+
| CoreConfig                              |
| new_match(seed, sides) -> State         |
| State: snakes, food, obstacles          |
+-----------------------------------------+
```

Text alternative: `CoreConfig` plus `seed` and `sides` produce `State`. `State` owns two `Snake` values, one `food` cell, and an obstacle set.

## Out of U1

`FeatureVector`, `Agent`, `MatchService`, `ExplanationPayload`, `config.yaml` I/O.
