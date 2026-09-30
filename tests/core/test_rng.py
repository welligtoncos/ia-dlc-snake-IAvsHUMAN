"""The stream registry is value-preserving (D48 item 2).

Two layers of protection. The composition tests spell out the `SeedSequence`
entries inline, so editing `rng.py` alone cannot change a stream silently.
The golden draws pin the actual numbers, so a numpy change that keeps the
composition but alters the bit stream also shows up here rather than as a
mysterious failure in a match test.
"""

from __future__ import annotations

import numpy as np

from snake_vs_machine.core import rng


def _draws(generator: np.random.Generator) -> list[int]:
    return [int(v) for v in generator.integers(0, 1000, 4)]


def test_obstacle_stream_composition() -> None:
    expected = np.random.default_rng(np.random.SeedSequence([7 + 3 * 1_000_003, 0]))
    assert _draws(rng.obstacle_generator(7, 3)) == _draws(expected)


def test_food_stream_composition() -> None:
    expected = np.random.default_rng(np.random.SeedSequence([7, 5]))
    assert _draws(rng.food_generator(7, 5)) == _draws(expected)


def test_helper_stream_composition() -> None:
    expected = np.random.default_rng(np.random.SeedSequence([7, 2_000_003]))
    assert _draws(rng.helper_generator(7)) == _draws(expected)


def test_agent_stream_composition() -> None:
    expected = np.random.default_rng(np.random.SeedSequence([7, 3_000_003, 5, 1]))
    assert _draws(rng.agent_generator(7, 5, 1)) == _draws(expected)


def test_golden_draws() -> None:
    assert _draws(rng.obstacle_generator(7, 3)) == [805, 675, 649, 907]
    assert _draws(rng.food_generator(7, 5)) == [558, 19, 994, 666]
    assert _draws(rng.helper_generator(7)) == [749, 370, 920, 727]
    assert _draws(rng.agent_generator(7, 5, 1)) == [574, 466, 670, 596]


def test_streams_are_mutually_distinct() -> None:
    """Same seed, four streams, four different draws — no tag collision."""
    streams = [
        _draws(rng.obstacle_generator(7, 0)),
        _draws(rng.food_generator(7, 1)),
        _draws(rng.helper_generator(7)),
        _draws(rng.agent_generator(7, 1, 0)),
    ]
    assert len({tuple(s) for s in streams}) == len(streams)


def test_agent_stream_separates_the_two_snakes() -> None:
    assert _draws(rng.agent_generator(7, 5, 0)) != _draws(rng.agent_generator(7, 5, 1))


def test_collection_seed_composition() -> None:
    expected = np.random.default_rng(np.random.SeedSequence([7, 4_000_003, 1, 3]))
    assert rng.collection_seed(7, 1, 3) == int(expected.integers(0, 2**31 - 1))


def test_dagger_seed_composition() -> None:
    expected = np.random.default_rng(np.random.SeedSequence([7, 5_000_003, 2, 4]))
    assert rng.dagger_seed(7, 2, 4) == int(expected.integers(0, 2**31 - 1))


def test_collection_and_dagger_seeds_are_distinct_from_the_u3_streams() -> None:
    seeds = {
        rng.collection_seed(7, 0, 0),
        rng.collection_seed(7, 1, 0),
        rng.dagger_seed(7, 1, 0),
        int(rng.helper_generator(7).integers(0, 2**31 - 1)),
    }
    assert len(seeds) == 4


def test_golden_collection_and_dagger_seeds() -> None:
    assert rng.collection_seed(7, 1, 3) == 891_526_738
    assert rng.dagger_seed(7, 2, 4) == 416_725_899


def test_trailing_zeros_are_invisible() -> None:
    """D56: length does not isolate streams."""
    a = np.random.SeedSequence([5]).generate_state(4)
    b = np.random.SeedSequence([5, 0]).generate_state(4)
    assert (a == b).all()


def test_stream_tags_are_unique_and_above_counters() -> None:
    assert len(set(rng.STREAM_TAGS)) == len(rng.STREAM_TAGS)
    assert rng.OBSTACLE_STRIDE == min(rng.STREAM_TAGS) - 1_000_000
    assert rng.OBSTACLE_STRIDE == 1_000_003
    assert all(tag > rng.OBSTACLE_STRIDE for tag in rng.STREAM_TAGS)
    from snake_vs_machine.core.state import CoreConfig

    assert CoreConfig().max_ticks < rng.OBSTACLE_STRIDE
    assert rng.MAX_MATCH_INDEX < rng.OBSTACLE_STRIDE


def test_ui_match_seed_composition() -> None:
    expected = np.random.default_rng(np.random.SeedSequence([7, 6_000_003, 3]))
    assert rng.ui_match_seed(7, 3) == int(expected.integers(0, 2**31 - 1))


def test_golden_ui_match_seed() -> None:
    assert rng.ui_match_seed(7, 3) == 1_975_942_399


def test_new_stream_tag_is_second_slot() -> None:
    """ui_match_seed: [session, tag, match_index] — tag is index 1."""
    assert 6_000_003 in rng.STREAM_TAGS
    assert 7_000_003 in rng.STREAM_TAGS
    assert 8_000_003 in rng.STREAM_TAGS


def test_tournament_seed_composition() -> None:
    expected = np.random.default_rng(np.random.SeedSequence([7, 7_000_003, 3]))
    assert rng.tournament_seed(7, 3) == int(expected.integers(0, 2**31 - 1))


def test_noise_generator_composition() -> None:
    expected = np.random.default_rng(np.random.SeedSequence([7, 8_000_003, 5, 1]))
    assert _draws(rng.noise_generator(7, 5, 1)) == _draws(expected)


def test_golden_tournament_and_noise() -> None:
    assert rng.tournament_seed(7, 3) == 1_859_932_336
    assert _draws(rng.noise_generator(7, 5, 1)) == [411, 843, 881, 516]
