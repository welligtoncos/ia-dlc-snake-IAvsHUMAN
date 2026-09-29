# U1 Core — NFR Requirements Plan

**Unit**: `u1-core`  
**Prerequisite**: Functional Design approved (D33)

## Execution checkboxes

- [x] Read U1 functional design (D31–D33)
- [x] Trace NFRs already locked in `requirements.md` / `decisions.md`
- [x] No new [Answer] questions — U1 NFRs are already decided (RNF01, RNF04, RNF05, RNF07, RNF09, RNF11, D30, D31)
- [x] Write `nfr-requirements.md`
- [x] Write `tech-stack-decisions.md`
- [x] Present two-option NFR completion (next: U1 NFR Design)
- [x] Approved with D34

## Locked (not re-asked)

| NFR | U1 implication |
| --- | --- |
| RNF01 | Python 3.11+; Windows, Linux, macOS |
| RNF04 | `seed` on every `new_match`; recorded on `State` |
| RNF05 | type hints on public APIs; `ruff`; `pytest`; Hypothesis PBT-02/03/07/08/09 |
| RNF07 | `core/` must not import pygame |
| RNF09 | `flood_fill_*` `limit=200` |
| RNF11 | `max_ticks=1800` |
| D30 | coverage ≥ 80% of `core/{state,setup,engine,queries}` |
| D31 | `SeedSequence`; no `hash()` |
| D09/D10 | Security and Resiliency baselines off |
| RNF02/RNF03 | Display FPS and 1000 games/min are **U3/U4** acceptances; U1 only keeps `step`/`new_match` clock-free and cheap enough not to block them |

## Questions

None. Ambiguities that would have been asked (coverage tool, Hypothesis budget, `step` microbench as U1 gate) are fixed in `tech-stack-decisions.md` as implementation defaults, not new product decisions.
