# U7 Explain + stress — Functional Design Plan

**Unit**: `u7-explain`
**Scope**: dicionário PT (D18 / RF05); render das 3 condições do `TreeExplanation.path`; `TimedAgent`; torneio 500; estresse; `reports/stress_results.md`; tabela Metrics aprovado/reprovado
**Depends on**: U2 `feature_names`; U3 `evaluation.batch` / `scoring` / `ExpertAgent`; U5 `TreeExplanation` / `PathStep` / models; U4 reserved RF05 stub
**Out of this unit**: VIPER / U6; RF08; retraining the product trees; `u7-done` tag unless asked
**NFR stages**: **pulados** (D27). Depois deste FD: **U7 Code Generation**.

No application code in this stage. Fill every `[Answer]:` below. Do not answer in chat.

## Execution checkboxes

- [x] Analyze unit context (`unit-of-work.md`, RF05, D12/D15/D18/D30, PRD stress table)
- [x] Collect answers in this file (`[Answer]:` tags)
- [x] Resolve ambiguities — Q3–Q6/Q8 extras fully specified; registered as D59
- [x] Write `aidlc-docs/construction/u7-explain/functional-design/domain-entities.md`
- [x] Write `aidlc-docs/construction/u7-explain/functional-design/business-rules.md`
- [x] Write `aidlc-docs/construction/u7-explain/functional-design/business-logic-model.md`
- [x] Write `aidlc-docs/construction/u7-explain/functional-design/frontend-components.md` (RF05 panel only)
- [x] Document PBT properties (labels round-trip, path slice, noise wrapper)
- [x] Present two-option Functional Design completion (next: U7 Code Generation)

## Locked (do not re-ask)

| Topic | Source |
| --- | --- |
| U7 **translates and renders** the U5 payload; it does not recompute `decision_path` | D30 / D45 |
| RF05: last move, **at most 3** conditions near the leaf; PT labels; veto visible (proposta vs executada) | RF05 / D15 |
| Panel default visible; **H** already toggles in U4 | D02 / D53 |
| Win score 1 / 0.5 / 0; draw rate reported separately | D14b |
| D12 500: BC-8 mask **on** vs BC-6 mask **off**, both vs expert, **+10 pp** | D12 |
| BC-8 mask on ≥ **40%** vs expert over 500 | D12 / D30 |
| Noise 10% drop ≤ **15 pp** | D30 / Metrics |
| U5 already **missed** some play bars (frozen BC-6 94.7%; 500 vs random 36.8% / 75.2%; latency 1.48 ms). Those numbers are facts | D52 |
| Scoring lives in `evaluation/scoring.py`; U7 may extend it (CI was deferred here in D48) | D48 |
| New RNG streams only in `core/rng.py` | D48 / D56: tag in **second** slot, ≠ existing tags |
| `ui` must not import `training` | D48 |
| NFR Requirements / Design **skipped** for U7 | D27 |
| No commit / tag unless asked | standing rule |

## U5 numbers U7 will re-report (not reinvent)

| Row | U5 close |
| --- | --- |
| Frozen BC-6 / BC-8 ≥ 95% | 94.7% / 96.5% |
| 500 vs random ≥ 90% | 36.8% / 75.2% |
| D12 100-match alert | recorded (gap 0.40; BC-8 mask vs expert was draws) |
| Inference < 1 ms | ALERTA 1.48 ms |

---

# Questions

## Question 1
Several Metrics rows already failed at U5 close. What is the U7 DoD for those rows?

A) Re-measure (or copy U5) and print **aprovado/reprovado** honestly. U7 DoD does **not** require turning a U5 miss into a pass

B) U7 DoD **fails** if any Metrics row is reprovado (would block closing this version)

C) U7 owns only D12-500, 40% vs expert, and noise ≤ 15 pp as blocking; every other Metrics row is informative

X) Other (please describe after [Answer]: tag below)

[Answer]:A — e o relatório ganha uma seção "Diagnóstico" com a tabela de causas de morte por modelo e a acurácia medida só nos estados críticos.

## Question 2
The PRD stress table is large (depth 1–15, noise ladder, sticky, delay, map sizes, obstacles, drop-one-feature, few-data, mask). What ships in U7?

A) **Full** table, 500 matches per cell, three product trees vs expert (very long)

B) **Blocking** cells only: D12 500, 40% vs expert, noise **10%** (≤ 15 pp). Other PRD rows: reduced N (e.g. 50) **or** marked skipped with a reason in `stress_results.md`

C) Full table but **N=50** everywhere (indicative; state that 500 is only on the blocking cells)

X) Other (please describe after [Answer]: tag below)

[Answer]:B — incluindo, em toda bateria, a tabela de causas de morte.

## Question 3
How is “10% noise on features” applied? The tree must not be refit.

A) A wrapper around any `Agent`: call `extract_features`, then with p=0.10 flip each **binary** feature and add Gaussian noise (σ documented, default 0.10) to each **continuous** feature; feed the noisy vector into `predict` + mask. Same seed stream for reproducibility

B) Mutate the live `State` (food/obstacles) with 10% chance — not the feature vector

C) Only flip bits; leave distances untouched

X) Other (please describe after [Answer]: tag below)

[Answer]:X — Opção A com três ajustes: valores contínuos com ruído são limitados ao intervalo [0, 1]; length_diff não recebe ruído; o ruído usa um stream novo no core/rng.py. Reportar a queda com máscara ligada e desligada (a máscara lê o estado real, não o vetor com ruído, então ela mascara o efeito do ruído).

## Question 4
RF05 path: U5 already stores the full `PathStep` tuple. Which slice and wording?

A) The **last 3** steps (closest to the leaf). Line: `{rótulo_PT} {'≤' if went_left else '>'} {threshold:.2f}` (value optional on a second column)

B) The **first 3** steps from the root, same wording

C) All steps; the panel scrolls if there are more than 3

X) Other (please describe after [Answer]: tag below)

[Answer]:X — Opção A (as 3 últimas condições, perto da folha), mostrando também o valor real da feature: "{rótulo} = {valor:.2f} ({'≤' ou '>'} {limiar:.2f})".

## Question 5
Where does the Portuguese dictionary live? Every `feature_names()` entry must have exactly one label.

A) `evaluation/labels_pt.py` — a frozen `dict[str, str]` imported by UI and tests (no YAML)

B) `ui/labels_pt.yaml` next to the font; UI loads it; evaluation tests read the same file

C) Hard-coded only inside `ui/render.py`

X) Other (please describe after [Answer]: tag below)

[Answer]:X — ui/labels_pt.py (dicionário Python, sem pygame). Teste em tests/ui: as chaves são exatamente feature_names(). Os relatórios da evaluation usam os nomes em inglês.

## Question 6
D48 left 95% CI and richer reports to U7. What does `evaluation/scoring.py` gain?

A) Wilson (or normal) 95% CI on the 1/0.5/0 mean; `stress_results.md` plots/tables use it

B) No CI this version — mean + draw rate only

C) Bootstrap CI (slower; N=500)

X) Other (please describe after [Answer]: tag below)

[Answer]:X — Intervalo normal com a variância amostral dos escores (1/0,5/0); para a D12, intervalo da DIFERENÇA entre as duas baterias. Aprovação pela estimativa pontual, como especificado; o intervalo é informativo.


## Question 7
`TimedAgent` (D44): clock stays out of `MatchService`.

A) `evaluation/timing.py`: wrap any `Agent` / `ExplainingAgent`; record wall time per `act`/`decide`; tournament writes mean ms into the report

B) No wrapper — keep using `scripts/bc_latency.py` / `expert_latency.py` only

C) Wrap **only** `TreeAgent`

X) Other (please describe after [Answer]: tag below)

[Answer]:A

## Question 8
Tournament / stress entry points and the RF05 code change.

A) `scripts/torneio.py` + `scripts/estresse.py`; RF05 text replaces the U4 stub in `ui/render.py` (same rectangle). New match seeds: tag **7_000_003** in `core/rng.py` (second slot, D56)

B) One `scripts/avaliacao.py` with subcommands; same UI and same new tag

C) pytest `slow` only — no extra scripts; RF05 in a new `ui/explain.py`

X) Other (please describe after [Answer]: tag below)

[Answer]: X — Opção A, com a formatação do texto do painel numa função pura (ui/explain_text.py) testada; render.py só desenha. Nova tag 7_000_003 para as seeds do torneio e 8_000_003 para o ruído.
