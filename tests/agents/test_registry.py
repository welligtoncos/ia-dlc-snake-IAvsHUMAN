"""AgentSpec must survive pickling, because Windows uses `spawn` (D48 item 1)."""

from __future__ import annotations

import pickle
from pathlib import Path

import pytest

from snake_vs_machine.agents.expert import ExpertAgent
from snake_vs_machine.agents.human import HumanAgent
from snake_vs_machine.agents.noisy import NoisyTreeAgent
from snake_vs_machine.agents.random_agent import RandomAgent
from snake_vs_machine.agents.registry import AgentSpec, build_agent
from snake_vs_machine.agents.tree import TreeAgent

_TINY = Path(__file__).resolve().parents[2] / "models" / "fixtures" / "tiny_depth3.joblib"


@pytest.mark.parametrize(
    ("name", "expected"),
    [("random", RandomAgent), ("expert", ExpertAgent), ("human", HumanAgent)],
)
def test_build_agent_returns_the_expected_type(name: str, expected: type) -> None:
    assert isinstance(build_agent(AgentSpec(name)), expected)


@pytest.mark.parametrize("name", ["random", "expert", "human"])
def test_spec_round_trips_through_pickle(name: str) -> None:
    spec = AgentSpec(name)
    restored = pickle.loads(pickle.dumps(spec))
    assert restored == spec
    assert isinstance(build_agent(restored), type(build_agent(spec)))


def test_unknown_agent_lists_the_known_names() -> None:
    with pytest.raises(
        ValueError,
        match="unknown agent 'nope'; known agents: expert, human, noisy_tree, random, tree",
    ):
        build_agent(AgentSpec("nope"))


def test_tree_spec_builds_and_survives_pickle() -> None:
    spec = AgentSpec("tree", {"path": str(_TINY), "safety_mask": True})
    restored = pickle.loads(pickle.dumps(spec))
    assert restored == spec
    agent = build_agent(restored)
    assert isinstance(agent, TreeAgent)


def test_noisy_tree_spec_builds_and_survives_pickle() -> None:
    spec = AgentSpec("noisy_tree", {"path": str(_TINY), "safety_mask": False})
    restored = pickle.loads(pickle.dumps(spec))
    assert restored == spec
    assert isinstance(build_agent(restored), NoisyTreeAgent)
