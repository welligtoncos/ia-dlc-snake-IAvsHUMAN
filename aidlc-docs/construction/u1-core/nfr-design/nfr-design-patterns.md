# U1 Core — NFR Design Patterns

Patterns for `core/` only. No cloud, pygame, or ML.

## Immutability (D34)

- `Cell`: `NamedTuple("Cell", [("x", int), ("y", int)])` — hashable for `frozenset`.
- `Snake`, `State`, `CoreConfig`: `@dataclass(frozen=True, slots=True)`.
- `body: tuple[Cell, ...]`; `obstacles: frozenset[Cell]`; occupancy returns `frozenset[Cell]`.
- `step` builds a **new** `State` via constructors / `replace`. Input object is never mutated.
- `copy(state)`: equality-preserving; may return `state` (already frozen) or `replace(state)`.
- **D35**: no `dict`/`list`/`set` inside `State`, `Snake`, or `CoreConfig`. Cobras e lados são `snake_a`/`snake_b` e `side_a`/`side_b` plus `snake(id)`. `hash(state)` works; field assign raises `FrozenInstanceError`.

## Deterministic entropy (D31, D34)

- `numpy.random.Generator` from `SeedSequence`. Exact **numpy version pinned** (NEP 19: `choice` / `shuffle` are not cross-version stable).
- Streams: obstacles `[seed_k, 0]`; food `[seed, tick]`; U1 random helper `[seed, 2000003]`.
- No `hash()`, no `random` module of the stdlib for match logic.

## Conservative vs real occupancy (D33)

- Shared `next_occupancy`; `step` passes real `opponent_action`.
- `is_fatal` / U2 / U3 omit it (superset occupancy — P-OCC-CONSERV).
- `is_fatal` False ⇒ `step` cannot assign wall / obstacle / body for any opponent action (P-FATAL).
- Optional (D35): `_body_cells(state)` computed once per `step` and reused in both `next_occupancy` calls.

## Layering (RNF07)

- `core/` imports only the stdlib and pinned `numpy`.
- Forbidden in U1 modules: `pygame`, `sklearn`, `joblib`, UI, I/O of models.

## Fail-fast setup

- Obstacle generation: 100 attempts then `SetupError`.
- Terminal `step`: identity snapshot, no exception.

## Test quality (D34)

| Control | Pattern |
| --- | --- |
| Hypothesis | `settings` profiles `dev` (100) and `full` (1000), `deadline=None`; select with `HYPOTHESIS_PROFILE` (default `dev`) |
| DoD | `HYPOTHESIS_PROFILE=full` before tag `u1-done` |
| Coverage | `pytest --cov --cov-branch`; ≥ 80% **branches** on U1 core files |
| Cache | `.hypothesis/` gitignored |
| Bench | Informative only; write `benchmark.md` with machine text; **not** a pytest fail |
| mypy | `mypy --strict` on `core/` optional |

## Performance (not a gate)

- No `sleep`, no clock, no I/O in `step` / `new_match` / queries.
- `flood_fill_count` returns exactly `min(reachable cells, limit)`, independent of visit order (D39).
- Bench records mean `step` time and random-helper games/min to support later RNF03 (U3).

## Resilience / scale / security

Not applied (D09, D10, desktop library). No retry loops, caches, or auth in U1.

```
+---------------------------+
| frozen State / Snake      |
| next_occupancy            |
| numpy Generator (pinned)  |
+---------------------------+
```

Text alternative: immutable values + shared occupancy + pinned numpy RNG.
