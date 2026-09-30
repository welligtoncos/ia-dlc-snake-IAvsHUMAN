"""Build agents from picklable descriptions (D48 item 1).

Windows uses the `spawn` start method, so a worker process cannot inherit a
live agent object — it receives a description and builds the agent locally.
That is why tasks carry an `AgentSpec` instead of an `Agent`.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from pathlib import Path

from snake_vs_machine.agents.base import Agent
from snake_vs_machine.agents.expert import ExpertAgent
from snake_vs_machine.agents.human import HumanAgent
from snake_vs_machine.agents.noisy import NoisyTreeAgent
from snake_vs_machine.agents.random_agent import RandomAgent
from snake_vs_machine.agents.tree import TreeAgent


@dataclass(frozen=True, slots=True)
class AgentSpec:
    """A name plus constructor parameters. Must stay picklable."""

    name: str
    params: Mapping[str, object] = field(default_factory=dict)


def _build_tree(*, path: object, safety_mask: object = False) -> TreeAgent:
    return TreeAgent.from_joblib(Path(str(path)), safety_mask=bool(safety_mask))


def _build_noisy_tree(*, path: object, safety_mask: object = False) -> NoisyTreeAgent:
    return NoisyTreeAgent(_build_tree(path=path, safety_mask=safety_mask))


_BUILDERS: dict[str, Callable[..., Agent]] = {
    "random": RandomAgent,
    "expert": ExpertAgent,
    "human": HumanAgent,
    "tree": _build_tree,
    "noisy_tree": _build_noisy_tree,
}


def build_agent(spec: AgentSpec) -> Agent:
    builder = _BUILDERS.get(spec.name)
    if builder is None:
        known = ", ".join(sorted(_BUILDERS))
        raise ValueError(f"unknown agent {spec.name!r}; known agents: {known}")
    return builder(**dict(spec.params))
