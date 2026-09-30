"""Behavior-cloning pipeline: collect, split, fit, DAgger (U5)."""

from snake_vs_machine.training.collect import collect
from snake_vs_machine.training.dagger import N_ITERATIONS, run_dagger
from snake_vs_machine.training.dataset import Dataset, load_npz, save_npz, split_by_match
from snake_vs_machine.training.fit import PRODUCT_DEPTHS, RANDOM_STATE, fit_product_trees

__all__ = [
    "N_ITERATIONS",
    "PRODUCT_DEPTHS",
    "RANDOM_STATE",
    "Dataset",
    "collect",
    "fit_product_trees",
    "load_npz",
    "run_dagger",
    "save_npz",
    "split_by_match",
]
