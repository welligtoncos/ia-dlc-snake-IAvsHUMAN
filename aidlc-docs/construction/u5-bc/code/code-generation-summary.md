# U5 Behavior Cloning — Code Generation Summary

**Unit**: `u5-bc`
**Plan**: `aidlc-docs/construction/plans/u5-bc-code-generation-plan.md`
**Decisions**: D50, D51, D52

## Created

```
src/snake_vs_machine/agents/tree.py
src/snake_vs_machine/training/{__init__,dataset,collect,fit,dagger}.py
scripts/{train_bc,bc_latency,build_bc_fixtures}.py
models/fixtures/{tiny_depth3,two_class,always_straight}.{joblib,json}
models/bc_depth{3,6,8}.{joblib,json}
tests/agents/{test_tree,test_tree_pbt}.py
tests/training/{test_dataset,test_collect,test_fit,test_dagger}.py
```

## Modified

```
src/snake_vs_machine/core/rng.py              # collection_seed, dagger_seed
src/snake_vs_machine/agents/{__init__,registry}.py
src/snake_vs_machine/evaluation/{batch,__init__}.py  # run_imap
tests/core/test_rng.py
tests/agents/test_registry.py
tests/evaluation/{test_batch,test_acceptance}.py
pyproject.toml                               # sklearn 1.9.1, joblib 1.6.0; mypy/coverage + training
```

## Quality

| Gate | Result |
| --- | --- |
| ruff | clean |
| mypy strict (`core`, `agents`, `services`, `evaluation`, `training`) | clean; sklearn/joblib `ignore_missing_imports` |
| pytest default | 166 passed without PBT files; full default includes tree PBT |
| `HYPOTHESIS_PROFILE=full` | **202 passed**, 2 deselected, **7m57s**, branch **97.83%** |

## Closing metrics (D52)

See `aidlc-docs/construction/u5-bc/benchmark.md`.

- Frozen test: BC-8 **96.5%** (pass); BC-6 **94.7%** (miss ≥ 95%)
- 500 vs random: BC-6 **36.8%**, BC-8 **75.2%** (both miss ≥ 90%)
- D12 100: gap 0.40 (alert); BC-8 mask-on vs expert was 100% draws
- Latency mask-on: **1.48 ms mean** — D40 **ALERTA** vs 1 ms
- Models written at U5 close; commit/tag `u5-done` only when asked

## Skipped layers

API, repository, frontend, database, deploy — N/A (desktop + offline train).
