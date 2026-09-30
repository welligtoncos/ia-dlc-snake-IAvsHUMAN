"""config.yaml load (P-UI-CFG)."""

from __future__ import annotations

from pathlib import Path

from snake_vs_machine.ui.config import load, parse_args


def test_missing_file_uses_defaults_and_draws_session_seed(tmp_path: Path) -> None:
    path = tmp_path / "nope.yaml"
    seen: list[str] = []
    cfg = load(path, bits=lambda n: 42, warn=seen.append)
    assert cfg.width == 20
    assert cfg.session_seed == 42
    assert cfg.models_dir == (tmp_path / "models").resolve()
    assert any("not found" in m for m in seen)
    assert any("session_seed 42" in m for m in seen)


def test_explicit_zero_session_seed_is_kept(tmp_path: Path) -> None:
    path = tmp_path / "c.yaml"
    path.write_text("session_seed: 0\nmodels_dir: trees\n", encoding="utf-8")
    cfg = load(path, bits=lambda n: 99)
    assert cfg.session_seed == 0
    assert cfg.models_dir == (tmp_path / "trees").resolve()


def test_invalid_field_falls_back(tmp_path: Path) -> None:
    path = tmp_path / "c.yaml"
    path.write_text("tick_rate: no\n", encoding="utf-8")
    seen: list[str] = []
    cfg = load(path, bits=lambda n: 1, warn=seen.append)
    assert cfg.tick_rate == 10
    assert any("tick_rate" in m for m in seen)


def test_parse_args_default_config() -> None:
    ns = parse_args([])
    assert ns.config == "config.yaml"
