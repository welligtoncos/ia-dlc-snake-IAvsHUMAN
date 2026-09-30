"""Train the three product BC trees (off the default pytest; D52)."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import joblib

from snake_vs_machine.agents.registry import AgentSpec
from snake_vs_machine.core.state import CoreConfig
from snake_vs_machine.evaluation.batch import MatchTask, run_imap, run_match
from snake_vs_machine.evaluation.scoring import BatteryScore, summarise
from snake_vs_machine.training.collect import collect
from snake_vs_machine.training.dagger import run_dagger
from snake_vs_machine.training.dataset import save_npz, split_by_match
from snake_vs_machine.training.fit import accuracy, fit_product_trees

_ROOT = Path(__file__).resolve().parents[1]
_DEFAULT_OUT = _ROOT / "models"


def _parse() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Behavior-cloning train + DAgger")
    parser.add_argument(
        "--fraction", type=float, default=1.0, help="Scale of min_rows / DAgger rows"
    )
    parser.add_argument("--min-rows", type=int, default=100_000)
    parser.add_argument("--dagger-rows", type=int, default=20_000)
    parser.add_argument("--dagger-iters", type=int, default=5)
    parser.add_argument("--vs-random-n", type=int, default=100)
    parser.add_argument("--acceptance-n", type=int, default=500)
    parser.add_argument("--d12-n", type=int, default=100)
    parser.add_argument("--batch-seed", type=int, default=1)
    parser.add_argument("--max-ticks", type=int, default=1800)
    parser.add_argument("--processes", type=int, default=None)
    parser.add_argument("--out-dir", type=Path, default=_DEFAULT_OUT)
    return parser.parse_args()


def _scale(value: int, fraction: float) -> int:
    return max(1, int(round(value * fraction)))


def _battery(
    path: Path,
    opponent: str,
    n: int,
    config: CoreConfig,
    mask: bool,
    processes: int | None,
) -> BatteryScore:
    spec_tree = AgentSpec("tree", {"path": str(path), "safety_mask": mask})
    spec_opp = AgentSpec(opponent)
    tasks = [MatchTask(spec_tree, spec_opp, config, seed) for seed in range(n)]
    return summarise(run_imap(run_match, tasks, processes=processes))


def main() -> None:
    args = _parse()
    if args.fraction <= 0:
        raise SystemExit("--fraction must be > 0")
    min_rows = _scale(args.min_rows, args.fraction)
    dagger_rows = _scale(args.dagger_rows, args.fraction)
    config = CoreConfig(max_ticks=args.max_ticks)
    out_dir: Path = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.perf_counter()
    print(
        f"collect min_rows={min_rows} fraction={args.fraction} processes={args.processes}",
        flush=True,
    )
    dataset = collect(min_rows, args.batch_seed, config, processes=args.processes)
    t_collect = time.perf_counter() - t0
    print(f"collect rows={len(dataset)} elapsed={t_collect:.1f}s", flush=True)

    train, test = split_by_match(dataset)
    save_npz(train, out_dir / "train.npz")
    save_npz(test, out_dir / "test.npz")
    n_test_matches = len(set(test.match_id.tolist()))
    print(f"split train={len(train)} test={len(test)} matches_test={n_test_matches}", flush=True)

    t1 = time.perf_counter()
    paths = fit_product_trees(train.X, train.y, out_dir)
    t_fit = time.perf_counter() - t1
    initial_acc = {
        depth: accuracy(joblib.load(path), test.X, test.y) for depth, path in paths.items()
    }
    print(f"fit elapsed={t_fit:.1f}s frozen_acc={initial_acc}", flush=True)

    t2 = time.perf_counter()
    train, paths, records = run_dagger(
        train,
        test,
        paths,
        batch_seed=args.batch_seed,
        target_rows=dagger_rows,
        config=config,
        vs_random_n=args.vs_random_n,
        n_iterations=args.dagger_iters,
        processes=args.processes,
    )
    t_dagger = time.perf_counter() - t2
    save_npz(train, out_dir / "train.npz")
    curve = [
        {
            "iteration": rec.iteration,
            "n_new_rows": rec.n_new_rows,
            "accuracy_frozen": rec.accuracy_frozen,
            "score_vs_random": rec.score_vs_random,
            "draw_vs_random": rec.draw_vs_random,
        }
        for rec in records
    ]
    print(f"dagger elapsed={t_dagger:.1f}s curve={curve}", flush=True)

    acceptance: dict[str, object] = {}
    if args.acceptance_n > 0:
        for depth in (6, 8):
            summary = _battery(
                paths[depth], "random", args.acceptance_n, config, False, args.processes
            )
            acceptance[f"bc{depth}_vs_random"] = {
                "n": args.acceptance_n,
                "score_rate_a": summary.score_rate_a,
                "draw_rate": summary.draw_rate,
            }
            print(f"acceptance BC-{depth}: {acceptance[f'bc{depth}_vs_random']}", flush=True)

    d12: dict[str, object] = {}
    if args.d12_n > 0:
        masked = _battery(paths[8], "expert", args.d12_n, config, True, args.processes)
        unmasked = _battery(paths[6], "expert", args.d12_n, config, False, args.processes)
        d12 = {
            "n": args.d12_n,
            "bc8_mask_on_vs_expert": {
                "score_rate_a": masked.score_rate_a,
                "draw_rate": masked.draw_rate,
            },
            "bc6_mask_off_vs_expert": {
                "score_rate_a": unmasked.score_rate_a,
                "draw_rate": unmasked.draw_rate,
            },
            "score_rate_gap": masked.score_rate_a - unmasked.score_rate_a,
        }
        print(f"d12 alert: {d12}", flush=True)

    report = {
        "fraction": args.fraction,
        "min_rows": min_rows,
        "dagger_rows": dagger_rows,
        "collect_s": t_collect,
        "fit_s": t_fit,
        "dagger_s": t_dagger,
        "elapsed_s": time.perf_counter() - t0,
        "n_train": len(train),
        "n_test": len(test),
        "initial_frozen_acc": initial_acc,
        "dagger_curve": curve,
        "acceptance": acceptance,
        "d12": d12,
    }
    report_path = out_dir / "train_report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {report_path}", flush=True)


if __name__ == "__main__":
    from multiprocessing import freeze_support

    freeze_support()
    main()
