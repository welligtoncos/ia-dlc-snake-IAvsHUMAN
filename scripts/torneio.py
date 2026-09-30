"""D12 500: BC-8 mask on vs expert, BC-6 mask off vs expert, paired seeds (D60)."""

from __future__ import annotations

import argparse
from pathlib import Path

from snake_vs_machine.agents.registry import AgentSpec
from snake_vs_machine.core.state import SnakeId
from snake_vs_machine.evaluation.batch import run_imap
from snake_vs_machine.evaluation.diagnostic import DEATH_LABELS, tree_death_cause
from snake_vs_machine.evaluation.paired import align_by_seeds, battery_tasks, tree_id, tree_scores
from snake_vs_machine.evaluation.scoring import normal_ci, paired_difference_ci
from snake_vs_machine.evaluation.timing import run_timed_match

_REPO = Path(__file__).resolve().parents[1]


def _death_row(name: str, causes: list[str], n: int) -> str:
    counts = {label: 0 for label in DEATH_LABELS}
    for cause in causes:
        counts[cause] = counts.get(cause, 0) + 1
    cells = [name] + [str(counts[label]) for label in DEATH_LABELS] + [str(n)]
    return "| " + " | ".join(cells) + " |"


def _fmt_ci(interval: tuple[float, float] | None) -> str:
    if interval is None:
        return "n/a (n<2)"
    return f"[{interval[0]:.3f}, {interval[1]:.3f}]"


def _run_battery(
    spec: AgentSpec, n: int, batch_seed: int, processes: int
) -> tuple[list[float], list[str], float]:
    tasks, seeds = battery_tasks(spec, n, batch_seed)
    timed = run_imap(run_timed_match, tasks, processes=processes)
    results = align_by_seeds([item[0] for item in timed], seeds)
    scores = tree_scores(results)
    causes = [tree_death_cause(result, tree_id(i)) for i, result in enumerate(results)]
    by_seed = {item[0].seed: item for item in timed}
    ms = [
        (by_seed[seed][1] if tree_id(index) is SnakeId.A else by_seed[seed][2])
        for index, seed in enumerate(seeds)
    ]
    mean_ms = sum(ms) / len(ms) if ms else float("nan")
    return scores, causes, mean_ms


def main() -> None:
    parser = argparse.ArgumentParser(description="D12 paired tournament")
    parser.add_argument("--n", type=int, default=500)
    parser.add_argument("--batch-seed", type=int, default=0)
    parser.add_argument("--processes", type=int, default=1)
    parser.add_argument("--models-dir", type=Path, default=_REPO / "models")
    args = parser.parse_args()
    models = args.models_dir
    spec8 = AgentSpec("tree", {"path": str(models / "bc_depth8.joblib"), "safety_mask": True})
    spec6 = AgentSpec("tree", {"path": str(models / "bc_depth6.joblib"), "safety_mask": False})
    print(
        f"D12 paired n={args.n} batch_seed={args.batch_seed} processes={args.processes}",
        flush=True,
    )
    scores8, causes8, ms8 = _run_battery(spec8, args.n, args.batch_seed, args.processes)
    scores6, causes6, ms6 = _run_battery(spec6, args.n, args.batch_seed, args.processes)
    mean8 = sum(scores8) / len(scores8)
    mean6 = sum(scores6) / len(scores6)
    gap = mean8 - mean6
    d12_ok = gap >= 0.10
    forty_ok = mean8 >= 0.40
    print(
        f"BC-8 mask on score_rate={mean8:.3f} mean_ms={ms8:.2f} "
        f"ci={_fmt_ci(normal_ci(scores8))}"
    )
    print(
        f"BC-6 mask off score_rate={mean6:.3f} mean_ms={ms6:.2f} "
        f"ci={_fmt_ci(normal_ci(scores6))}"
    )
    print(
        f"paired gap={gap:.3f} ci={_fmt_ci(paired_difference_ci(scores8, scores6))} "
        f"D12(+10pp)={'aprovado' if d12_ok else 'reprovado'} "
        f"BC-8>=40%={'aprovado' if forty_ok else 'reprovado'}"
    )
    print("| model | " + " | ".join(DEATH_LABELS) + " | n |")
    print("| --- | " + " | ".join("---" for _ in DEATH_LABELS) + " | --- |")
    print(_death_row("BC-8 mask on", causes8, args.n))
    print(_death_row("BC-6 mask off", causes6, args.n))


if __name__ == "__main__":
    main()
