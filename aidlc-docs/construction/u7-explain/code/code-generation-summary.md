# U7 Explain + stress — Code Generation Summary

**Decisions**: D59 (FD), D60 (paired design). NFR stages skipped (D27).

## Created

- `src/snake_vs_machine/agents/noisy.py`
- `src/snake_vs_machine/evaluation/timing.py`
- `src/snake_vs_machine/evaluation/noise.py` (re-export)
- `src/snake_vs_machine/evaluation/diagnostic.py`
- `src/snake_vs_machine/evaluation/paired.py`
- `src/snake_vs_machine/ui/labels_pt.py`
- `src/snake_vs_machine/ui/explain_text.py`
- `scripts/torneio.py`
- `scripts/estresse.py`
- `reports/stress_results.md`
- tests: `test_labels_pt`, `test_explain_text`, `test_timing`, `test_noise`, `test_diagnostic`, `test_paired`, `test_u7_pbt`

## Modified

- `core/rng.py` — tags `7_000_003` / `8_000_003`; `tournament_seed(batch, match_index)`; `noise_generator`
- `agents/tree.py` — `decide_from_vector`
- `agents/registry.py` — `noisy_tree`
- `evaluation/scoring.py` — `normal_ci`, `difference_ci`, `paired_difference_ci`
- `evaluation/batch.py` — D60 Pool note
- `evaluation/__init__.py` — CI exports
- `ui/render.py` — blits `explain_text.lines`
- `scripts/u7_diagnostico.py` — thin CLI

## Commands

```text
python scripts/torneio.py --n 500 --batch-seed 0 --processes 1
python scripts/estresse.py --n 200 --batch-seed 0 --processes 1 --diagnostico
```

## Metrics (from `reports/stress_results.md`)

| Cell | Verdict |
| --- | --- |
| D12 +10 pp (gap 0.422) | aprovado |
| BC-8 ≥ 40% (0.500) | aprovado |
| Noise ≤ 15 pp (drops 0.440 / 0.480) | reprovado |
| U5 frozen / vs-random / latency | unchanged (94.7% miss; 36.8% / 75.2%; ALERTA 1.48 ms) |
| RNF03 | aprovado herdado (U3 4918.8; D60) |

## Quality

- ruff clean; mypy strict 43 files
- pytest `--cov --cov-branch`: **276 passed**, **85.33%** (omit `render.py`)

## Out of unit

VIPER; retrain; `u7-done` tag unless asked.
