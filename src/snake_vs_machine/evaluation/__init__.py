"""Evaluation: scoring and batch batteries (U3; extended by U7)."""

from snake_vs_machine.evaluation.batch import (
    MatchTask,
    by_seed,
    run_imap,
    run_match,
    run_parallel,
    run_sequential,
)
from snake_vs_machine.evaluation.scoring import (
    BatteryScore,
    difference_ci,
    match_score,
    normal_ci,
    paired_difference_ci,
    summarise,
)

__all__ = [
    "BatteryScore",
    "MatchTask",
    "by_seed",
    "difference_ci",
    "match_score",
    "normal_ci",
    "paired_difference_ci",
    "run_imap",
    "run_match",
    "run_parallel",
    "run_sequential",
    "summarise",
]
