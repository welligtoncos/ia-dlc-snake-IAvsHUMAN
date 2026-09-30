# U5 Behavior Cloning — Benchmark

## D51 pin

| Package | Version |
| --- | --- |
| numpy | 2.2.6 |
| scikit-learn | 1.9.1 |
| joblib | 1.6.0 |

mypy: `ignore_missing_imports` for `sklearn.*` and `joblib` (no stub extra).

## Etapa 15 — 5% probe (D52 item 2)

```text
python scripts/train_bc.py --fraction 0.05 --out-dir models/probe --vs-random-n 8 --acceptance-n 0 --d12-n 0 --processes 1
```

| Step | Result |
| --- | --- |
| collect | 11 738 rows in **16.3 s** |
| fit 3/6/8 | **0.04 s** |
| DAgger ×5 | **31.0 s** |
| wall | **47.4 s** |
| ×20 estimate | **~20–40 min** — proceeded |

## Etapa 16 — Hypothesis full

`HYPOTHESIS_PROFILE=full`: **202 passed**, 2 deselected (`slow`) in **7m57s**. Branch coverage **97.83%**.

## Etapa 17 — full train (D52 item 1)

```text
python scripts/train_bc.py --fraction 1.0 --out-dir models
```

Wall **46.4 min** (collect 37.9 s + fit 1.6 s + DAgger 42.6 min + 500-match + D12).

| Dataset | Rows | Notes |
| --- | --- | --- |
| collect | 123 848 | min_rows=100 000; long matches overshoot |
| train after DAgger | 205 812 | +~20 k × 5 |
| frozen test | 23 202 | **13** `match_id`s only (80/20 by match) |

### Frozen-test accuracy (never used to pick hyperparameters)

| After | BC-3 | BC-6 | BC-8 |
| --- | ---: | ---: | ---: |
| initial fit | 67.7% | 92.4% | **96.2%** |
| DAgger 1 | 68.9% | 94.1% | **96.1%** |
| DAgger 2 | 68.9% | 94.0% | **96.1%** |
| DAgger 3 | 68.2% | 94.3% | **96.1%** |
| DAgger 4 | 60.4% | **96.1%** | **96.1%** |
| DAgger 5 (final) | 61.1% | 94.7% | **96.5%** |

Bar ≥ 95% for BC-6 and BC-8: **BC-8 yes; BC-6 no** (94.7%; was 96.1% at iter 4).

### DAgger vs-random (N=100, draw rate 0)

| Iter | BC-3 | BC-6 | BC-8 |
| ---: | ---: | ---: | ---: |
| 1 | 0.00 | 0.49 | 0.63 |
| 2 | 0.00 | 0.32 | 0.50 |
| 3 | 0.13 | 0.27 | 0.60 |
| 4 | 0.23 | 0.71 | 0.89 |
| 5 | 0.16 | 0.35 | 0.79 |

### Acceptance 500 vs `RandomAgent` (mask off, draw rate 0)

| Model | score_rate_a | Bar ≥ 90% |
| --- | ---: | --- |
| BC-6 | **36.8%** | missed |
| BC-8 | **75.2%** | missed |

### D12 alert (100 matches, does not gate U5)

| Pairing | score_rate_a | draw_rate |
| --- | ---: | ---: |
| BC-8 mask on vs expert | 0.50 | **1.00** (all draws) |
| BC-6 mask off vs expert | 0.10 | 0.00 |
| score-rate gap | 0.40 | — |

### Inference latency (D40 ALERTA)

`scripts/bc_latency.py` on `models/bc_depth8.joblib`, mask on, kickoff, n=200:

| mean | max | 1 ms |
| ---: | ---: | --- |
| **1.48 ms** | 2.24 ms | **ALERTA** |

## Closing bar (D52)

| Criterion | Result |
| --- | --- |
| Frozen ≥ 95% BC-6 / BC-8 | BC-8 **pass**; BC-6 **fail** (94.7%) |
| 500 vs random ≥ 90% BC-6 / BC-8 | both **fail** (36.8% / 75.2%) |
| DAgger curve recorded | yes |
| D12 100-match alert recorded | yes |
| Latency vs 1 ms | **ALERTA** 1.48 ms |
| Models at U5 close | `models/bc_depth{3,6,8}.joblib` + JSON |
