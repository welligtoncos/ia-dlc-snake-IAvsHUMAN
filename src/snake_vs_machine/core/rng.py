"""Single registry of every deterministic RNG stream (D48 item 2, D56).

A new stream may only be added in this module. Spreading `SeedSequence`
composition across call sites is how two streams silently start sharing a
tag. The tag of a **new** stream always occupies the **second** entropy
slot and must differ from every existing tag.

Trailing zeros in a `SeedSequence` entropy vector are invisible (D56):
`SeedSequence([5]).generate_state(4)` equals
`SeedSequence([5, 0]).generate_state(4)`. Vector **length** does not isolate
streams.

The compositions below are **value-preserving** for streams that existed
before U4. Changing one changes every match ever generated from a given
seed, so the U1 determinism, golden vector and replay tests are the guard
against an accidental edit.

`1_000_003` is the obstacle **stride**, not a position-2 tag.

Known fragility: the food stream is `[seed, tick_after]` (no tag). Because
trailing zeros vanish, `[seed, 0]` equals `[seed]`, which equals
`[seed_k, 0]` when `seed_k == seed`. `tick_after` is therefore never 0
(respawn after a completed tick, so `tick_after >= 1`).

Counters that can sit in a tag-like slot (`tick` / `tick_after` <=
`max_ticks`, `match_index` < 1_000_000) stay strictly below `1_000_003`.
"""

from __future__ import annotations

import numpy as np

_OBSTACLE_STRIDE = 1_000_003
_HELPER_TAG = 2_000_003
_AGENT_TAG = 3_000_003
_COLLECTION_TAG = 4_000_003
_DAGGER_TAG = 5_000_003
_UI_MATCH_TAG = 6_000_003
_TOURNAMENT_TAG = 7_000_003
_NOISE_TAG = 8_000_003

# Public so tests can lock the D56 invariant without importing privates.
STREAM_TAGS: tuple[int, ...] = (
    _HELPER_TAG,
    _AGENT_TAG,
    _COLLECTION_TAG,
    _DAGGER_TAG,
    _UI_MATCH_TAG,
    _TOURNAMENT_TAG,
    _NOISE_TAG,
)
OBSTACLE_STRIDE = _OBSTACLE_STRIDE
MAX_MATCH_INDEX = 1_000_000


def obstacle_generator(seed: int, attempt: int) -> np.random.Generator:
    """Obstacle placement, attempt `attempt` of the retry loop (D31)."""
    seed_k = int(seed + attempt * _OBSTACLE_STRIDE)
    return np.random.default_rng(np.random.SeedSequence([seed_k, 0]))


def food_generator(seed: int, tick_after: int) -> np.random.Generator:
    """Food respawn after the tick that produced `tick_after` (D32)."""
    return np.random.default_rng(np.random.SeedSequence([int(seed), int(tick_after)]))


def helper_generator(seed: int) -> np.random.Generator:
    """U1 random-match test helper (BR-A2)."""
    return np.random.default_rng(np.random.SeedSequence([int(seed), _HELPER_TAG]))


def agent_generator(seed: int, tick: int, snake_index: int) -> np.random.Generator:
    """Agent draw for one snake on one tick (D44 item 3).

    `snake_index` is 0 for snake A and 1 for snake B, passed explicitly by the
    caller — never read from `SnakeId`'s `auto()` value.
    """
    return np.random.default_rng(
        np.random.SeedSequence([int(seed), _AGENT_TAG, int(tick), int(snake_index)])
    )


def collection_seed(batch_seed: int, pairing_code: int, match_index: int) -> int:
    """Integer seed for one collection match (D52).

    `pairing_code` is 0 for expert vs expert and 1 for expert vs random.
    The value is fed to `new_match` / `play`; it is not a Generator.
    """
    rng = np.random.default_rng(
        np.random.SeedSequence(
            [int(batch_seed), _COLLECTION_TAG, int(pairing_code), int(match_index)]
        )
    )
    return int(rng.integers(0, 2**31 - 1))


def dagger_seed(batch_seed: int, iteration: int, match_index: int) -> int:
    """Integer seed for one DAgger match (D52 item 3)."""
    rng = np.random.default_rng(
        np.random.SeedSequence(
            [int(batch_seed), _DAGGER_TAG, int(iteration), int(match_index)]
        )
    )
    return int(rng.integers(0, 2**31 - 1))


def ui_match_seed(session_seed: int, match_index: int) -> int:
    """Integer seed for one UI match (D55 / D56). Tag in the second slot."""
    rng = np.random.default_rng(
        np.random.SeedSequence(
            [int(session_seed), _UI_MATCH_TAG, int(match_index)]
        )
    )
    return int(rng.integers(0, 2**31 - 1))


def tournament_seed(batch_seed: int, match_index: int) -> int:
    """Integer seed for one tournament/stress match (D59 / D60).

    No pairing_code: batteries in the same comparison share this list.
    Tag in the second slot.
    """
    rng = np.random.default_rng(
        np.random.SeedSequence(
            [int(batch_seed), _TOURNAMENT_TAG, int(match_index)]
        )
    )
    return int(rng.integers(0, 2**31 - 1))


def noise_generator(seed: int, tick: int, snake_index: int) -> np.random.Generator:
    """Feature-noise draws for one snake on one tick (D59 item 2)."""
    return np.random.default_rng(
        np.random.SeedSequence(
            [int(seed), _NOISE_TAG, int(tick), int(snake_index)]
        )
    )
