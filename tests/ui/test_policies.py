"""PolicyId → AgentSpec."""

from __future__ import annotations

from pathlib import Path

from snake_vs_machine.ui.policies import PolicyId, label, spec_for


def test_labels_are_portuguese() -> None:
    assert label(PolicyId.hard) == "Difícil"
    assert label(PolicyId.random) == "Aleatório"


def test_tree_spec_uses_models_dir_and_mask() -> None:
    root = Path("C:/models")
    easy = spec_for(PolicyId.easy, root)
    hard = spec_for(PolicyId.hard, root)
    assert easy.name == "tree"
    assert easy.params["path"] == str(root / "bc_depth3.joblib")
    assert easy.params["safety_mask"] is False
    assert hard.params["safety_mask"] is True
    assert spec_for(PolicyId.random, root).name == "random"


def test_easy_joblib_loads() -> None:
    from snake_vs_machine.agents.registry import build_agent

    spec = spec_for(PolicyId.easy, Path("models"))
    agent = build_agent(spec)
    assert type(agent).__name__ == "TreeAgent"
