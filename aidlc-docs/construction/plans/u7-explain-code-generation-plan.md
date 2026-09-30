# U7 Explain + stress — Code Generation Plan

**Unit**: `u7-explain`
**Type**: brownfield add-on — RF05 text, scoring CI, noise wrapper, TimedAgent, tournament/stress scripts
**This file is the only source of truth for U7 code generation.**
**Approved** with **D60** (paired seeds, paired CI, noise N=200, Windows Pool note).

## Unit context

| Item | Value |
| --- | --- |
| Stories | Skipped; map is RF05 / D12 / Metrics → U7 in `unit-of-work-story-map.md` |
| Implements | RF05 (PT path + veto); D12 500; BC-8 ≥ 40% vs expert; noise 10% ≤ 15 pp; Metrics aprovado/reprovado; Diagnóstico |
| Depends on | U2 `feature_names` / `extract_features`; U3 `play` / `batch` / `scoring` / `ExpertAgent`; U5 `TreeAgent` / `TreeExplanation` / `PathStep`; U4 HUD rectangle + H toggle |
| Does not include | VIPER / U6; RF08; retraining; flipping U5 play-bar misses; `u7-done` unless asked |
| NFR stages | **Skipped** (D27) |
| API / repository / database / deploy | **Skip** — desktop + CLI reports |
| Frontend | RF05 text only. `data-testid` **N/A** (Pygame) |

## Locked design (D59)

1. `stress_results.md` **Diagnóstico**: death-cause table per model + critical-state accuracy (fatal-any **or** expert ≠ `straight`). Pre-CG N=50 snapshot already in `domain-entities.md`.
2. Noise: wrapper A; continuous clip [0, 1]; `length_diff` untouched; tag **8_000_003**; drop with mask on **and** off (mask reads real `State`).
3. Panel: last 3 `path` steps; `{rótulo} = {valor:.2f} ({≤|>} {limiar:.2f})` in `ui/explain_text.py`.
4. `ui/labels_pt.py` no pygame; test `keys == feature_names()`. Evaluation reports stay English.
5. `scoring.py`: normal CI from sample variance of {1, 0.5, 0}; **`paired_difference_ci`** (D60) for D12 and noise; pass/fail by **point** estimate.
6. Tournament seed tag **7_000_003**, form `tournament_seed(batch, match_index)` — **no** `pairing_code` (D60); scripts `torneio.py` + `estresse.py`; stub replaced in the U4 rectangle.
7. DoD: honest Metrics; blocking = D12-500, 40% vs expert, noise 10%; `TimedAgent` in `evaluation/timing.py`.
8. D56: new tags in the **second** slot; add both to `STREAM_TAGS`.
9. `ui` must not import `training` or `evaluation`.

## Paths (application code NEVER under `aidlc-docs/`)

```
src/snake_vs_machine/core/rng.py              # modified: tournament_seed, noise_generator
src/snake_vs_machine/agents/tree.py           # modified: decide_from_vector
src/snake_vs_machine/agents/registry.py       # modified: noisy_tree spec
src/snake_vs_machine/evaluation/scoring.py    # modified: CI + difference CI
src/snake_vs_machine/evaluation/timing.py     # created
src/snake_vs_machine/evaluation/noise.py      # created
src/snake_vs_machine/evaluation/diagnostic.py # created
src/snake_vs_machine/evaluation/__init__.py   # modified exports
src/snake_vs_machine/ui/labels_pt.py          # created
src/snake_vs_machine/ui/explain_text.py       # created
src/snake_vs_machine/ui/render.py             # modified: blit explain_text lines

scripts/torneio.py
scripts/estresse.py
scripts/u7_diagnostico.py                     # thin wrap of diagnostic (already exists)

tests/core/test_rng.py                        # modified: tags 7/8
tests/agents/test_tree.py                     # decide_from_vector
tests/evaluation/test_scoring.py              # CI
tests/evaluation/test_timing.py
tests/evaluation/test_noise.py
tests/evaluation/test_diagnostic.py
tests/evaluation/test_u7_pbt.py
tests/ui/test_labels_pt.py
tests/ui/test_explain_text.py
tests/agents/test_registry.py                 # noisy_tree if needed

reports/stress_results.md                     # written by scripts (workspace root, not aidlc-docs)
```

Docs only: `aidlc-docs/construction/u7-explain/code/code-generation-summary.md`

## Execution steps

- [x] **Etapa 1 — RNG tags (D56 + D59 item 6 + D60)**: Add `_TOURNAMENT_TAG = 7_000_003` and `_NOISE_TAG = 8_000_003` to `STREAM_TAGS`. `tournament_seed(batch_seed, match_index)`: `SeedSequence([batch, 7_000_003, match_index])` then `integers(0, 2**31-1)` — **no** `pairing_code`. `noise_generator(seed, tick, snake_index)`: `SeedSequence([seed, 8_000_003, tick, snake_index])`. Tests: composition + golden + uniqueness; both tags > `OBSTACLE_STRIDE` and in slot 2. Existing U1–U6 rng goldens stay green.

- [x] **Etapa 2 — `TreeAgent.decide_from_vector`**: Extract the predict / proba / `_path_steps` / `_apply_mask` body from `decide`. `decide` becomes `extract_features` → `decide_from_vector`. Path and `proposed` use the **given** vector; mask still uses the **real** `State`. Existing tree tests stay green. Needed so noise does not copy sklearn calls.

- [x] **Etapa 3 — `ui/labels_pt.py` (P-LAB-KEYS)**: Frozen `LABELS_PT: dict[str, str]` with **exactly** these keys (wording vetoable at the gate):

  | key | pt |
  | --- | --- |
  | danger_ahead | perigo à frente |
  | danger_left | perigo à esquerda |
  | danger_right | perigo à direita |
  | dist_danger_ahead | dist. perigo à frente |
  | dist_danger_left | dist. perigo à esquerda |
  | dist_danger_right | dist. perigo à direita |
  | space_free_ahead | espaço livre à frente |
  | space_free_left | espaço livre à esquerda |
  | space_free_right | espaço livre à direita |
  | food_ahead | comida à frente |
  | food_left | comida à esquerda |
  | food_right | comida à direita |
  | food_behind | comida atrás |
  | dist_food | dist. comida |
  | opponent_closer_to_food | oponente mais perto da comida |
  | dist_opponent_head | dist. cabeça oponente |
  | head_risk_ahead | risco de cabeça à frente |
  | head_risk_left | risco de cabeça à esquerda |
  | head_risk_right | risco de cabeça à direita |
  | length_diff | diferença de comprimento |

  `tests/ui/test_labels_pt.py`: `set(LABELS_PT) == set(feature_names())` and no pygame import (`"pygame" not in sys.modules` after import, or inspect the module). No silent English fallback.

- [x] **Etapa 4 — `ui/explain_text.py` (P-XPL-N, P-XPL-FMT)**: Pure functions, no pygame. `lines(explanation: TreeExplanation) -> tuple[str, ...]` = veto block (`proposta` / `executada` / `vetado: sim|não`) plus last `min(3, len(path))` conditions formatted `f"{LABELS_PT[name]} = {value:.2f} ({op} {threshold:.2f})"` with `op` `≤` if `went_left` else `>`. Missing key **raises** (KeyError). Empty path → veto lines only. `lines(None)` is not this function's job (`render` prints `sem explicação`). Tests construct `PathStep` / `TreeExplanation` without joblib.

- [x] **Etapa 5 — `render.py`**: Replace the stub string builder with `explain_text.lines(explain)` when `explain` is not None. Cache key includes the returned tuple. Hidden panel still empty rect. No logic besides blit. Coverage omit stays.

- [x] **Etapa 6 — `scoring.py` CI (P-CI-WIDE, D60)**: `normal_ci(scores) -> tuple[float, float] | None` = mean ± 1.96 * sqrt(sample_var / n), `ddof=1`. `None` when `n < 2`. `paired_difference_ci(xs, ys)` requires equal length: mean of `(x_i - y_i)` ± 1.96 * s_d / √n. Length mismatch → `ValueError`. Keep unpaired `difference_ci` as a helper. Tests: known lists; n=1 → None; paired example.

- [x] **Etapa 7 — `evaluation/timing.py`**: `TimedAgent` wraps any `Agent`. If the inner has `decide`, so does the wrapper (`ExplainingAgent`). Record wall time per `act` / `decide` (one list). `mean_ms` property. Does **not** sit in `MatchService`. Test with a fake agent that sleeps 0 (or a stub clock injected — prefer `time.perf_counter` and a dummy whose `act` is cheap; assert list length, not a time floor).

- [x] **Etapa 8 — `evaluation/noise.py` + registry**: Binary names = `danger_*`, `food_*`, `head_risk_*`, `opponent_closer_to_food`. Continuous = the rest except `length_diff` (never noised). `apply_noise(vector, names, rng) -> list[float]`: flip binaries with p=0.10; add N(0, 0.10) to continuous then clip [0, 1]. `NoisyTreeAgent(tree: TreeAgent)`: `decide` extracts real features, noises via `noise_generator(state.seed, state.tick, snake_index)`, calls `decide_from_vector`. Mask remains on real state. Register `AgentSpec` name `noisy_tree` with `path`, `safety_mask`, so Windows `spawn` workers can build it. Tests: P-NOI-CLIP, P-NOI-DET; `length_diff` identical; clip bounds.

- [x] **Etapa 9 — `evaluation/diagnostic.py`**: `tree_death_cause(result, tree_id) -> str` (`DeathCause.name` or `"timeout"`). `is_critical(state, snake_id, expert) -> bool`. `critical_hit(executed, expert_action)`. Counters / accuracy helpers used by scripts. Move the body of `scripts/u7_diagnostico.py` here; the script becomes a thin `if __name__` CLI (ASCII headers only — no `≠` on Windows cp1252). Unit tests with synthetic `MatchResult` + a tiny in-memory tree or recorded actions (no 50-match run in pytest).

- [x] **Etapa 10 — `scripts/torneio.py`**: D12, N default **500**. **Same** `tournament_seed(batch, i)` list for BC-8 mask on and BC-6 mask off (D60). Sides alternate by `i` (tree A even / B odd). `TimedAgent` on both sides. Print score rates, draw rates, point pass/fail (gap ≥ 10 pp; BC-8 ≥ 40%), `normal_ci` per battery, **`paired_difference_ci`**, death-cause tables, mean ms. `--n`, `--batch-seed`, `--processes` (default **1**, D60). Worker in `evaluation`.

- [x] **Etapa 11 — `scripts/estresse.py`**: Noise N default **200** (D60). Four batteries share **one** seed list: clean/noisy × mask on/off (BC-8 unless `--model`). Drop = clean − noisy (pp) per mask; pass if each drop ≤ 15 pp **and** N ≥ 200. If N < 200, mark the cell **indicativa** (not blocking). `paired_difference_ci` on the paired scores. Death-cause table every battery. Other PRD rows: **Skipped** list. `--diagnostico` N=50 via Etapa 9. Writes `reports/stress_results.md`.

- [x] **Etapa 12 — Run batteries + `reports/stress_results.md`**: **First show** the N=50 Diagnóstico tables (D60 item 5). Then `torneio.py` N=500 and `estresse.py` N=200 + Diagnóstico. Metrics (U5 copy + new rows, honest pass/fail); D12 with paired CI; noise with paired CI; Diagnóstico snapshot + re-run. Do not invent numbers.

- [x] **Etapa 13 — PBT**: `tests/evaluation/test_u7_pbt.py` and/or UI tests: P-LAB-KEYS (already exact-set), P-XPL-N, P-XPL-FMT, P-NOI-CLIP, P-NOI-DET, P-CI-WIDE. Profiles `dev` / `full`. Hypothesis strategies reuse existing `playing_state` where useful.

- [x] **Etapa 14 — Quality gates**: `ruff` clean; mypy strict on existing packages (new `evaluation` / `ui` modules included automatically). `pytest --cov --cov-branch` ≥ 80% with `render.py` still omitted. Import check: `ui.labels_pt` and `ui.explain_text` do not import `training` or `evaluation`. Existing U1–U5 suite stays green. Default pytest does **not** run N=500.

- [x] **Etapa 15 — Markdown summary**: `aidlc-docs/construction/u7-explain/code/code-generation-summary.md` — created vs modified, tags 7/8, battery commands, Metrics pass/fail copied from `reports/stress_results.md`.

- [x] **Etapa 16 — Skipped layers**: API, repository, database, deploy, web `data-testid`, Infrastructure Design, U7 NFR — N/A.

## Plan decisions you can veto at the gate

| Decision | Why | Alternative |
| --- | --- | --- |
| `decide_from_vector` on `TreeAgent` | One sklearn path; mask stays on real state | Duplicate predict inside `NoisyTreeAgent` |
| Noise N=**200** paired (D60) | Blocking size; N<200 = indicativa | N=50 or N=500 |
| `--processes` default 1 | D60 Windows Pool hang (U5); U3 parallel still valid for RNF03 | `cpu_count - 1` |
| PT wording in the Etapa 3 table | Closed dictionary; easy to bikeshed | You supply a different table |
| Shared seed list, no pairing_code | D60 paired design | Separate streams per battery |
| Pre-CG Diagnóstico shown before Etapa 12, then re-run | D60 item 5 | Snapshot only |

## Traceability

| Design source | Plan step |
| --- | --- |
| D59 item 1 Diagnóstico | 9, 11, 12 |
| D59 item 2 noise + tag 8 | 1, 2, 8, 11 |
| D59 items 3–4 RF05 | 3, 4, 5 |
| D59 item 5 scoring CI | 6 |
| D59 item 6 tags 7 + scripts | 1, 10, 11 |
| D59 item 7 TimedAgent + honest Metrics | 7, 10, 12 |
| D56 tag slot 2 | 1 |
| PBT-02/03/07/08/09 | 3, 4, 8, 13 |
| D12 / D25 / D30 | 10, 12 |

## Out of this unit

Retrain; VIPER; `u7-done` tag — only after you approve the generated code and explicitly ask for it. Next stage after U7 CG approval: **Build e Testes**.
