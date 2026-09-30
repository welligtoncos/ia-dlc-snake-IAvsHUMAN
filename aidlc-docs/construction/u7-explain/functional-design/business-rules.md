# U7 Explain + stress — Business Rules

## RF05 (D15, D18, D59 items 3–4)

| ID | Rule |
| --- | --- |
| BR-X7-1 | U7 does not recompute `decision_path`. It only formats `TreeExplanation`. |
| BR-X7-2 | Conditions shown: last min(3, len(path)) `PathStep`s. |
| BR-X7-3 | Line format: `{rótulo} = {valor:.2f} ({≤ if went_left else >} {limiar:.2f})`. |
| BR-X7-4 | `rótulo` comes from `ui/labels_pt.py`. Missing key is a test failure, not a silent English fallback. |
| BR-X7-5 | Veto block stays: `proposta` / `executada` / `vetado: sim\|não` (U4 stub fields), now plus the path lines. |
| BR-X7-6 | `explain_text.py` is importable without pygame. `render.py` only blits. |

## Metrics and DoD (D59 items 1, 7)

| ID | Rule |
| --- | --- |
| BR-M7-1 | Every Metrics row is **aprovado** or **reprovado** from the point estimate. U7 DoD does not require flipping U5 misses. |
| BR-M7-2 | Blocking U7 batteries: D12 500 (+10 pp), BC-8 mask-on ≥ 40% vs expert, noise 10% drop ≤ 15 pp. |
| BR-M7-3 | Other PRD stress rows: N≈50 or skipped, with a reason. Every run battery still prints a **death-cause** table. |
| BR-M7-4 | Diagnóstico: death-cause table per model + critical-state accuracy (fatal-any **or** expert ≠ straight). |

## Noise (D59 item 2)

| ID | Rule |
| --- | --- |
| BR-N7-1 | Wrapper: `extract_features` → noise → `predict` / mask. Tree is not refit. |
| BR-N7-2 | Binary features: flip with p=0.10. Continuous: N(0, 0.10) then clip to [0, 1]. |
| BR-N7-3 | `length_diff` is never noised. |
| BR-N7-4 | Mask uses real occupancy / `is_fatal`, not the noisy vector. |
| BR-N7-5 | Report the drop **mask on** and **mask off**. |
| BR-N7-6 | Noise RNG only via tag `8_000_003` in `core/rng.py`. |

## Scoring (D59 item 5)

| ID | Rule |
| --- | --- |
| BR-S7-1 | 95% CI: normal, using the **sample variance** of per-match scores {1, 0.5, 0}. |
| BR-S7-2 | D12: CI of the **difference** of the two battery means (BC-8 mask on minus BC-6 mask off, both vs expert). |
| BR-S7-3 | Pass/fail uses the **point** estimate only. CI is informative. |

## Tournament (D59 item 6)

| ID | Rule |
| --- | --- |
| BR-T7-1 | Match seeds from `tournament_seed` (tag `7_000_003`). |
| BR-T7-2 | Scripts: `scripts/torneio.py`, `scripts/estresse.py`. |
| BR-T7-3 | `TimedAgent` in `evaluation/timing.py` wraps any agent; mean ms goes into the report. |

## Layering

| ID | Rule |
| --- | --- |
| BR-L7-1 | `ui` does not import `training`. |
| BR-L7-2 | Evaluation reports use English feature names. |
