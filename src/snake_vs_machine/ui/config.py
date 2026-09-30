"""Load `config.yaml` without pygame (D54 / D55)."""

from __future__ import annotations

import argparse
import secrets
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

_DEFAULTS: dict[str, Any] = {
    "width": 20,
    "height": 20,
    "tick_rate": 10,
    "cell_px": 24,
    "hud_width": 280,
    "obstacle_count": 0,
    "panel_key": "H",
    "models_dir": "models",
}


@dataclass(frozen=True, slots=True)
class UiConfig:
    width: int
    height: int
    tick_rate: int
    cell_px: int
    hud_width: int
    obstacle_count: int
    panel_key: str
    models_dir: Path
    session_seed: int
    config_path: Path


BitsFn = Callable[[int], int]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="jogo")
    parser.add_argument("--config", default="config.yaml")
    return parser.parse_args(argv)


def _as_int(value: object, default: int, warnings: list[str], name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        try:
            return int(str(value))
        except ValueError:
            warnings.append(f"invalid {name}, using {default}")
            return default
    return value


def load(
    path: Path,
    *,
    bits: BitsFn = secrets.randbits,
    warn: Callable[[str], None] | None = None,
) -> UiConfig:
    warnings: list[str] = []
    data: dict[str, Any] = {}
    raw: object
    if not path.is_file():
        warnings.append(f"config not found: {path}")
    else:
        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError) as exc:
            warnings.append(f"invalid config {path}: {exc}")
            raw = None
        if raw is None:
            data = {}
        elif not isinstance(raw, dict):
            warnings.append("config root must be a mapping")
        else:
            data = raw

    parent = path.resolve().parent
    width = _as_int(data.get("width", _DEFAULTS["width"]), 20, warnings, "width")
    height = _as_int(data.get("height", _DEFAULTS["height"]), 20, warnings, "height")
    tick_rate = _as_int(
        data.get("tick_rate", _DEFAULTS["tick_rate"]), 10, warnings, "tick_rate"
    )
    cell_px = _as_int(data.get("cell_px", _DEFAULTS["cell_px"]), 24, warnings, "cell_px")
    hud_width = _as_int(
        data.get("hud_width", _DEFAULTS["hud_width"]), 280, warnings, "hud_width"
    )
    obstacle_count = _as_int(
        data.get("obstacle_count", _DEFAULTS["obstacle_count"]),
        0,
        warnings,
        "obstacle_count",
    )
    panel_key = str(data.get("panel_key", _DEFAULTS["panel_key"]))
    models_rel = str(data.get("models_dir", _DEFAULTS["models_dir"]))
    models_dir = (parent / models_rel).resolve()

    if "session_seed" not in data:
        session_seed = int(bits(31))
        warnings.append(f"session_seed {session_seed}")
    else:
        session_seed = _as_int(data["session_seed"], 0, warnings, "session_seed")

    if warn is not None:
        for message in warnings:
            warn(message)

    return UiConfig(
        width=width,
        height=height,
        tick_rate=tick_rate,
        cell_px=cell_px,
        hud_width=hud_width,
        obstacle_count=obstacle_count,
        panel_key=panel_key,
        models_dir=models_dir,
        session_seed=session_seed,
        config_path=path,
    )
