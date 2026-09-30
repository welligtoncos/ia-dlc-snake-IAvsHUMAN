# U7 Explain + stress — Domain Entities

Technology-agnostic except types already shipped (`TreeExplanation`, `PathStep`, `MatchResult`, `feature_names`).

## Packages

```text
evaluation/timing.py      # TimedAgent (Q7=A)
evaluation/scoring.py     # + normal CI, difference CI (D59 item 5)
evaluation/noise.py       # feature-noise wrapper (CG)
ui/labels_pt.py           # PT dictionary, no pygame (D59 item 4)
ui/explain_text.py        # pure RF05 strings (D59 item 3)
ui/render.py              # draws strings only
core/rng.py               # tags 7_000_003 (tournament), 8_000_003 (noise)
scripts/torneio.py
scripts/estresse.py
reports/stress_results.md
```

`evaluation` reports stay in **English** identifiers. The UI dictionary is Portuguese.

## FeatureLabel

| Field | Meaning |
| --- | --- |
| `name` | English key from `feature_names()` |
| `pt` | Exactly one Portuguese string in `LABELS_PT` |

Keys of `LABELS_PT` **equal** `feature_names()` (test in `tests/ui`).

## PathLine

One RF05 line, from a `PathStep` after translation:

`{rótulo} = {valor:.2f} ({≤|>} {limiar:.2f})`

At most **3** lines: the **last** three `PathStep`s (nearest the leaf). Empty path → no condition lines (stub `sem explicação` if no `TreeExplanation`).

## NoiseSpec

| Field | Rule |
| --- | --- |
| `p_flip` | 0.10 on binary features |
| `sigma` | 0.10 Gaussian on continuous features, then **clip [0, 1]** |
| `skip` | `length_diff` is never noised |
| `stream` | `SeedSequence([seed, 8_000_003, tick, snake_index])` |
| `mask` | `safety_mask` still uses the **real** `State` / `is_fatal` |

## TournamentSeed

`tournament_seed(batch_seed, pairing_code, match_index)` → int via `integers`, tag **7_000_003** in the second slot (D56).

## Diagnostic tables (D59 item 1)

Preview **before CG** (`scripts/u7_diagnostico.py`, 2026-09-30): N=50 vs expert, sides alternating, product masks (BC-3/6 off, BC-8 on). Cause is the **tree** snake (`death_cause_a`/`_b`); timeout if `EndReason.timeout` or cause is None.

| model | wall | obstacle | self_body | opponent_body | head_to_head | timeout | n |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| BC-3 | 5 | 0 | 9 | 11 | 24 | 1 | 50 |
| BC-6 | 7 | 0 | 14 | 24 | 0 | 5 | 50 |
| BC-8 | 0 | 0 | 0 | 0 | 0 | 50 | 50 |

Critical = some action `is_fatal` **or** expert ≠ `straight`. Hit = tree's executed action equals `ExpertAgent.act` on that tick.

| model | hits | critical | accuracy |
| --- | ---: | ---: | ---: |
| BC-3 | 1109 | 1395 | 79.5% |
| BC-6 | 2568 | 2991 | 85.9% |
| BC-8 | 24457 | 27729 | 88.2% |

U7 CG copies this section into `reports/stress_results.md` Diagnóstico (re-run or keep these N=50 numbers as the pre-CG snapshot).

## TimedAgent

Wraps `Agent` / `ExplainingAgent`. Records wall time per `act` / `decide`. Does not sit inside `MatchService`.

## Out of this unit

VIPER; retraining; making U5 play bars pass.
