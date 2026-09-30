# U7 Explain + stress — Business Logic Model

## RF05 line

```text
steps = explanation.path[-3:]
for step in steps:
    label = LABELS_PT[step.feature_name]
    op = "≤" if step.went_left else ">"
    emit f"{label} = {step.feature_value:.2f} ({op} {step.threshold:.2f})"
```

Text alternative: take the last three path steps; look up the Portuguese label; show the live feature value and the inequality that was taken.

## Critical state (diagnóstico)

A pre-tick `(state, snake_id)` is **critical** iff:

- `is_fatal(state, snake_id, a)` is true for some `a` in `{straight, turn_left, turn_right}`, **or**
- `ExpertAgent.act(state, snake_id) ≠ straight`

Accuracy on that set: fraction of states where `TreeAgent.act` equals `ExpertAgent.act`.

## Noise wrapper

```text
v = extract_features(state, snake_id)
for i, name in enumerate(feature_names()):
    if name == "length_diff":
        continue
    if name is binary:
        with p=0.10: v[i] = 1 - v[i]
    else:
        v[i] = clip(v[i] + N(0, 0.10), 0, 1)
predict(v); mask using real state
```

Binary names (U2): the 0/1 flags (`danger_*`, `food_*`, `head_risk_*`, `opponent_closer_to_food`). Distances and `space_free_*` are continuous. `length_diff` skipped.

## D12 difference CI

Let `x_i`, `y_j` be per-match scores of the two batteries. Point gap = `mean(x) - mean(y)`.  
SE ≈ `sqrt(s_x²/n_x + s_y²/n_y)`. Interval: gap ± 1.96 SE. Pass if `mean(x) ≥ mean(y) + 0.10`.

## Tournament match

```text
seed = tournament_seed(batch, pairing, i)   # tag 7_000_003
play(tree_spec, expert_spec, config, seed, sides)
```

Sides alternate by `i` (D25).

## Propriedades testáveis

| ID | Target | Property |
| --- | --- | --- |
| P-LAB-KEYS | `LABELS_PT` | `set(keys) == set(feature_names())` |
| P-XPL-N | `explain_text` | at most 3 lines; order is the tail of `path` |
| P-XPL-FMT | `explain_text` | `≤` iff `went_left` |
| P-NOI-CLIP | noise | continuous outputs ∈ [0, 1]; `length_diff` unchanged |
| P-NOI-DET | noise | same `(state, seed, tick, side)` → same noisy vector |
| P-CI-WIDE | scoring | n=1 → interval degenerates in a documented way (skip or infinite) |

## Judgement (veto at the gate)

| Call | Choice |
| --- | --- |
| Binary vs continuous split | flags 0/1 vs the rest, except `length_diff` skipped |
| Diagnóstico N before CG | 50 matches / model vs expert, product masks (3 off, 6 off, 8 on) |
