# U2 Features — Code Generation Plan (seed)

**Unit**: `u2-features`  
**Status**: seed from U1 close-out. Expand during U2 Code Generation Part 1.  
**This file is the carry-forward list U2 CG must include.**

## Locked tasks (from U1 `u1-done`)

- [ ] **Remove** `omit = ["*/features.py"]` from `pyproject.toml` (`[tool.coverage.run]`). After `core/features.py` exists, the `fail_under = 80` branch gate applies to **all** of `snake_vs_machine.core` (BR-A3, D30).

## Unit context (to complete in U2 CG Part 1)

| Item | Value |
| --- | --- |
| Implements | `extract_features`, `space_free_*`, PBT rotation/mirror |
| Depends on | U1 (`flood_fill_count`, `reachable_cells`, `State`) |
| Does not include | agents, MatchService, UI, tree models |
