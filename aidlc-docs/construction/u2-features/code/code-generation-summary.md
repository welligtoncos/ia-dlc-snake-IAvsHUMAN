# U2 Features — Code Generation Summary

**Unit**: `u2-features`  
**TDD**: `test_features.py` collected with `ModuleNotFoundError` before `features.py` existed.

## Public APIs

| Symbol | Meaning |
| --- | --- |
| `extract_features(state, snake_id)` | 20-tuple or `ValueError` if dead/terminal |
| `feature_names()` | English names, sklearn column order |
| `FEATURE_SCHEMA_VERSION` | `1` (U5 persists / rejects mismatch) |

Private helper `_free_cell_count(state, me, opp)` supplies the `space_free_*` denominator (D42); not part of the U2 public surface.

No numpy inside `features.py`. Space uses `flood_fill_count` only.

## How to test

```text
pytest
pytest --cov --cov-branch
set HYPOTHESIS_PROFILE=full
pytest tests/core/test_features_pbt.py
```

Last run: **79 passed**, **96.97%** branch coverage of all `core/` (`omit` of `features.py` removed).

## D39 / D40 / D41 / D42 / D43

- Golden kickoff A + fairness A==B
- Transform helpers: `rot90`×4, mirrors×2, kickoff `rot180` swaps bodies
- PBT from `new_match` + `step`; board rotate/mirror; `_free_cell_count` oracle (D42)
- `free_cells` computed once per call by arithmetic; `_space` takes it as a parameter (D42)
- `danger` from `_blocked` with the reused occupancy; P-FEAT-DANGER PBT pins it to `is_fatal` (D43)
- U1 `reachable_cells` BFS rewritten over integer indices; public signature unchanged (D43)
- Bench kickoff: **4.11 → 2.12 → 0.543 → 0.415 ms**, now **OK** vs 0.5 ms; shared flood (step 3) not needed
- `HYPOTHESIS_PROFILE=full`: 79 passed in 4m05s, branch coverage 96.97%

## Out of U2

Agents, UI, `u2-done` tag (after you approve and ask). `HYPOTHESIS_PROFILE=full` before that tag.

## Extension compliance

| Rule | Status |
| --- | --- |
| PBT-02/03/07/08/09 | Conform |
| Security / Resiliency | N/A (disabled) |
