# U2 Features — NFR Requirements Plan

**Unit**: `u2-features`  
**Prerequisite**: Functional Design approved (D38, D39)

## Execution checkboxes

- [x] Read U2 functional design (D38–D39)
- [x] Trace NFRs already locked (RNF05, RNF07, RNF09, RNF10, D30, D34, D37)
- [x] No new [Answer] questions — U2 NFRs inherit U1 stack; D39 adds test/count contracts only
- [x] Write `nfr-requirements.md`
- [x] Write `tech-stack-decisions.md`
- [x] Present two-option NFR completion (next: U2 NFR Design)
- [x] Approved with D40

## Locked (not re-asked)

| NFR / decision | U2 implication |
| --- | --- |
| RNF01 / D37 | Python ≥ 3.13 |
| RNF05 | hints, ruff, pytest, Hypothesis P-FEAT-* |
| RNF07 | `core/features.py` must not import pygame or sklearn |
| RNF08 | English `feature_names()` |
| RNF09 / D39 | Features call `flood_fill_count` (`limit=200`) only; not order-dependent `reachable_cells` |
| RNF10 | This unit **is** the feature vector |
| D30 / D36 | After CG, ≥ 80% branch of all `core/` including `features.py` (drop `omit`) |
| D34 | numpy pin unused in features module (tuple out); Hypothesis `dev`/`full` |
| D38 | `FEATURE_SCHEMA_VERSION`; `ValueError` if dead/terminal |
| D39 | Golden vector; fairness A==B; U1 flood-count isometry test |
| D09/D10 | Security and Resiliency off |
| RNF02/RNF03 | No clock in `extract_features`; bench informative (not a pytest fail) |

## Questions

None.
