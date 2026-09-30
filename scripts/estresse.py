"""Noise 10% paired batteries + optional diagnostico (D59 / D60)."""

from __future__ import annotations

import argparse
from pathlib import Path

from snake_vs_machine.agents.registry import AgentSpec
from snake_vs_machine.evaluation.batch import run_imap
from snake_vs_machine.evaluation.diagnostic import (
    DEATH_LABELS,
    run_product_diagnostic,
    tree_death_cause,
)
from snake_vs_machine.evaluation.paired import align_by_seeds, battery_tasks, tree_id, tree_scores
from snake_vs_machine.evaluation.scoring import paired_difference_ci
from snake_vs_machine.evaluation.timing import run_timed_match

_REPO = Path(__file__).resolve().parents[1]
_NOISE_BLOCKING_N = 200
_SKIPPED = (
    "depth ladder 1-15 (not shipped this version)",
    "sticky / delay / map sizes / obstacles variants",
    "drop-one-feature / few-data",
)


def _death_row(name: str, causes: list[str], n: int) -> str:
    counts = {label: 0 for label in DEATH_LABELS}
    for cause in causes:
        counts[cause] += 1
    cells = [name] + [str(counts[label]) for label in DEATH_LABELS] + [str(n)]
    return "| " + " | ".join(cells) + " |"


def _fmt_ci(interval: tuple[float, float] | None) -> str:
    if interval is None:
        return "n/a (n<2)"
    return f"[{interval[0]:.3f}, {interval[1]:.3f}]"


def _run(
    spec: AgentSpec, n: int, batch_seed: int, processes: int
) -> tuple[list[float], list[str]]:
    tasks, seeds = battery_tasks(spec, n, batch_seed)
    timed = run_imap(run_timed_match, tasks, processes=processes)
    results = align_by_seeds([item[0] for item in timed], seeds)
    scores = tree_scores(results)
    causes = [tree_death_cause(result, tree_id(i)) for i, result in enumerate(results)]
    return scores, causes


def _print_diagnostic(models_dir: Path, n: int) -> None:
    print(f"\n## Diagnostico N={n} vs expert, product masks", flush=True)
    rows = run_product_diagnostic(n, models_dir)
    print("| model | " + " | ".join(DEATH_LABELS) + " | n |")
    print("| --- | " + " | ".join("---" for _ in DEATH_LABELS) + " | --- |")
    for row in rows:
        cells = [row.name] + [str(row.deaths[label]) for label in DEATH_LABELS] + [str(n)]
        print("| " + " | ".join(cells) + " |")
    print("| model | hits | critical | accuracy |")
    print("| --- | ---: | ---: | ---: |")
    for row in rows:
        print(f"| {row.name} | {row.hits} | {row.critical} | {row.accuracy:.1%} |")


def write_report(
    path: Path,
    n: int,
    drops: dict[str, float],
    cis: dict[str, str],
    blocking: bool,
    d12_lines: str,
) -> None:
    status = "bloqueante" if blocking else "indicativa (N<200)"
    verdict = {}
    for key, drop in drops.items():
        if not blocking:
            verdict[key] = "indicativa"
        else:
            verdict[key] = "aprovado" if drop <= 0.15 else "reprovado"
    path.parent.mkdir(parents=True, exist_ok=True)
    body = [
        "# stress_results",
        "",
        "## Noise 10% (D59 / D60)",
        "",
        f"N={n} paired. Cell status: **{status}**.",
        "",
        f"- mask on drop={drops['on']:.3f} paired_ci={cis['on']} → {verdict['on']}",
        f"- mask off drop={drops['off']:.3f} paired_ci={cis['off']} → {verdict['off']}",
        "",
        "## D12 (see also scripts/torneio.py)",
        "",
        d12_lines or "(run torneio.py to fill)",
        "",
        "## Skipped PRD rows",
        "",
    ]
    body.extend(f"- {item}" for item in _SKIPPED)
    body.append("")
    path.write_text("\n".join(body) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Paired noise stress")
    parser.add_argument("--n", type=int, default=_NOISE_BLOCKING_N)
    parser.add_argument("--batch-seed", type=int, default=0)
    parser.add_argument("--processes", type=int, default=1)
    parser.add_argument("--models-dir", type=Path, default=_REPO / "models")
    parser.add_argument("--diagnostico", action="store_true")
    parser.add_argument("--diagnostico-n", type=int, default=50)
    parser.add_argument(
        "--report",
        type=Path,
        default=_REPO / "reports" / "stress_results.md",
    )
    args = parser.parse_args()
    model = args.models_dir / "bc_depth8.joblib"
    clean_on = AgentSpec("tree", {"path": str(model), "safety_mask": True})
    noisy_on = AgentSpec("noisy_tree", {"path": str(model), "safety_mask": True})
    clean_off = AgentSpec("tree", {"path": str(model), "safety_mask": False})
    noisy_off = AgentSpec("noisy_tree", {"path": str(model), "safety_mask": False})
    blocking = args.n >= _NOISE_BLOCKING_N
    print(
        f"noise paired n={args.n} blocking={blocking} "
        f"batch_seed={args.batch_seed} processes={args.processes}",
        flush=True,
    )
    s_con, c_con = _run(clean_on, args.n, args.batch_seed, args.processes)
    s_non, c_non = _run(noisy_on, args.n, args.batch_seed, args.processes)
    s_coff, c_coff = _run(clean_off, args.n, args.batch_seed, args.processes)
    s_noff, c_noff = _run(noisy_off, args.n, args.batch_seed, args.processes)
    drop_on = sum(s_con) / len(s_con) - sum(s_non) / len(s_non)
    drop_off = sum(s_coff) / len(s_coff) - sum(s_noff) / len(s_noff)
    print(f"mask on drop={drop_on:.3f} ci={_fmt_ci(paired_difference_ci(s_con, s_non))}")
    print(f"mask off drop={drop_off:.3f} ci={_fmt_ci(paired_difference_ci(s_coff, s_noff))}")
    print("| battery | " + " | ".join(DEATH_LABELS) + " | n |")
    print("| --- | " + " | ".join("---" for _ in DEATH_LABELS) + " | --- |")
    print(_death_row("clean mask on", c_con, args.n))
    print(_death_row("noisy mask on", c_non, args.n))
    print(_death_row("clean mask off", c_coff, args.n))
    print(_death_row("noisy mask off", c_noff, args.n))
    write_report(
        args.report,
        args.n,
        {"on": drop_on, "off": drop_off},
        {
            "on": _fmt_ci(paired_difference_ci(s_con, s_non)),
            "off": _fmt_ci(paired_difference_ci(s_coff, s_noff)),
        },
        blocking,
        "",
    )
    print(f"wrote {args.report}")
    if args.diagnostico:
        _print_diagnostic(args.models_dir, args.diagnostico_n)


if __name__ == "__main__":
    main()
