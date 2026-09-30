"""Kickoff inference latency: extract_features + decide with the mask on (D40)."""

from __future__ import annotations

import argparse
import time
from pathlib import Path

from snake_vs_machine.agents.tree import TreeAgent
from snake_vs_machine.core.features import extract_features
from snake_vs_machine.core.setup import new_match
from snake_vs_machine.core.state import CoreConfig, SnakeId

_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=Path, default=_ROOT / "models" / "bc_depth8.joblib")
    parser.add_argument("--repeats", type=int, default=200)
    args = parser.parse_args()
    agent = TreeAgent.from_joblib(args.path, safety_mask=True)
    state = new_match(CoreConfig(obstacle_count=0), seed=0)
    # Warm-up so the first joblib/sklearn hit is not in the sample.
    extract_features(state, SnakeId.A)
    agent.decide(state, SnakeId.A)
    samples: list[float] = []
    for _ in range(args.repeats):
        start = time.perf_counter()
        extract_features(state, SnakeId.A)
        agent.decide(state, SnakeId.A)
        samples.append((time.perf_counter() - start) * 1000.0)
    mean = sum(samples) / len(samples)
    peak = max(samples)
    flag = "ALERTA" if mean >= 1.0 else "ok"
    print(f"n={len(samples)} mean_ms={mean:.4f} max_ms={peak:.4f} alerta_1ms={flag}")


if __name__ == "__main__":
    main()
