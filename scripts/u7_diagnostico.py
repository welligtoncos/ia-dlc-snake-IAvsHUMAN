"""Thin CLI over evaluation.diagnostic.run_product_diagnostic (D59 item 1)."""

from __future__ import annotations

import argparse
from pathlib import Path

from snake_vs_machine.evaluation.diagnostic import DEATH_LABELS, run_product_diagnostic

_REPO = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=50)
    parser.add_argument("--models-dir", type=Path, default=_REPO / "models")
    args = parser.parse_args()
    print(f"N={args.n} vs expert, alternating sides, product masks\n", flush=True)
    rows = run_product_diagnostic(args.n, args.models_dir)
    print("## Death causes (tree snake)")
    print("| model | " + " | ".join(DEATH_LABELS) + " | n |")
    print("| --- | " + " | ".join("---" for _ in DEATH_LABELS) + " | --- |")
    for row in rows:
        cells = [row.name] + [str(row.deaths[label]) for label in DEATH_LABELS] + [str(args.n)]
        print("| " + " | ".join(cells) + " |")
    print("\n## Critical-state accuracy (fatal-any or expert != straight)")
    print("| model | hits | critical | accuracy |")
    print("| --- | ---: | ---: | ---: |")
    for row in rows:
        print(f"| {row.name} | {row.hits} | {row.critical} | {row.accuracy:.1%} |")


if __name__ == "__main__":
    main()
