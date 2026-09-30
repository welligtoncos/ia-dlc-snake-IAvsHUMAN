# stress_results

Honest Metrics (D59 Q1=A). Pass/fail is the **point** estimate. CIs are informative (D60).

## Metrics

| Row | Number | Verdict |
| --- | --- | --- |
| Frozen BC-6 ≥ 95% | 94.7% (U5) | **reprovado** |
| Frozen BC-8 ≥ 95% | 96.5% (U5) | **aprovado** |
| 500 vs random BC-6 ≥ 90% | 36.8% (U5) | **reprovado** |
| 500 vs random BC-8 ≥ 90% | 75.2% (U5) | **reprovado** |
| Inference vs 1 ms | 1.48 ms kickoff (U5) | **ALERTA** |
| D12 500: BC-8 mask on − BC-6 mask off ≥ +10 pp | gap **0.422** | **aprovado** |
| BC-8 mask on vs expert ≥ 40% | **0.500** | **aprovado** |
| Noise 10% drop ≤ 15 pp, mask on | drop **0.440** | **reprovado** |
| Noise 10% drop ≤ 15 pp, mask off | drop **0.480** | **reprovado** |
| RNF03 ≥ 1000/min random vs random | 4918.8 (U3 parallel) | **aprovado** (herdado; D60) |

U7 blocking cells: D12 and 40% **pass**; noise **fails**. U5 misses stay misses.

## D12 (N=500, paired seeds, D60)

`python scripts/torneio.py --n 500 --batch-seed 0 --processes 1`

| Battery | score_rate | mean_ms | normal 95% CI |
| --- | ---: | ---: | --- |
| BC-8 mask on vs expert | 0.500 | 0.86 | [0.500, 0.500] |
| BC-6 mask off vs expert | 0.078 | 0.94 | [0.055, 0.101] |

Paired gap (BC-8 − BC-6) = **0.422**, `paired_difference_ci` = **[0.399, 0.445]**.

Death causes (tree snake):

| model | wall | obstacle | self_body | opponent_body | head_to_head | timeout | n |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| BC-8 mask on | 0 | 0 | 0 | 0 | 0 | 500 | 500 |
| BC-6 mask off | 45 | 0 | 200 | 211 | 7 | 37 | 500 |

BC-8: every match timed out (score 0.5). Same pattern as the U5 N=100 alert (all draws).

## Noise 10% (N=200, paired, blocking)

`python scripts/estresse.py --n 200 --batch-seed 0 --processes 1`

Cell status: **bloqueante**. Tree = BC-8. Drop = clean − noisy (score points).

| Mask | drop | paired 95% CI | Verdict |
| --- | ---: | --- | --- |
| on | 0.440 | [0.407, 0.473] | **reprovado** (> 15 pp) |
| off | 0.480 | [0.461, 0.499] | **reprovado** (> 15 pp) |

| battery | wall | obstacle | self_body | opponent_body | head_to_head | timeout | n |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| clean mask on | 0 | 0 | 0 | 0 | 0 | 200 | 200 |
| noisy mask on | 6 | 0 | 24 | 12 | 146 | 12 | 200 |
| clean mask off | 0 | 0 | 0 | 0 | 0 | 200 | 200 |
| noisy mask off | 50 | 0 | 37 | 41 | 68 | 4 | 200 |

Clean BC-8 vs expert timed out in all 200 seeds (mask on and off). Noise breaks that stalemate, mostly via head-to-head.

## Diagnóstico (N=50 vs expert, product masks)

Pre-CG snapshot and Etapa 12 re-run are **identical** (same seeds `0..49`, same joblibs).

| model | wall | obstacle | self_body | opponent_body | head_to_head | timeout | n |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| BC-3 | 5 | 0 | 9 | 11 | 24 | 1 | 50 |
| BC-6 | 7 | 0 | 14 | 24 | 0 | 5 | 50 |
| BC-8 | 0 | 0 | 0 | 0 | 0 | 50 | 50 |

Critical = some action `is_fatal` **or** expert ≠ `straight`. Hit = tree executed action equals expert.

| model | hits | critical | accuracy |
| --- | ---: | ---: | ---: |
| BC-3 | 1109 | 1395 | 79.5% |
| BC-6 | 2568 | 2991 | 85.9% |
| BC-8 | 24457 | 27729 | 88.2% |

## Skipped PRD rows

- depth ladder 1–15 (not shipped this version)
- sticky / delay / map sizes / obstacles variants
- drop-one-feature / few-data
