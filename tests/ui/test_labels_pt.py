"""P-LAB-KEYS: dictionary keys are exactly feature_names() (D59 item 4)."""

from __future__ import annotations

import inspect

from snake_vs_machine.core.features import feature_names
from snake_vs_machine.ui import labels_pt


def test_keys_match_feature_names() -> None:
    assert set(labels_pt.LABELS_PT) == set(feature_names())


def test_module_source_does_not_import_pygame() -> None:
    source = inspect.getsource(labels_pt)
    assert "import pygame" not in source
    assert "from pygame" not in source


def test_labels_and_explain_do_not_import_training_or_evaluation() -> None:
    from snake_vs_machine.ui import explain_text

    for module in (labels_pt, explain_text):
        source = inspect.getsource(module)
        assert "snake_vs_machine.training" not in source
        assert "snake_vs_machine.evaluation" not in source
