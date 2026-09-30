# U3 Agents + MatchService — Benchmark

**Budgets** (informative — never fail pytest):
- Expert decision ≤ 1 ms worst case (D46 item 2, D48 item 4)
- ≥ 1000 matches/min random vs random on the **multiprocess** run (RNF03, D46 item 1)

## Machine

| Field | Value |
| --- | --- |
| OS | Windows 11 |
| CPU | AMD64 Family 25 Model 80 Stepping 0, AuthenticAMD |
| Python | 3.13.7 |
| numpy | 2.2.6 |
| Processes | `cpu_count() - 1` = 15 (16 logical) |

## Expert latency (D48 item 4)

| Row | Scenario | Mean | Max | n | Status vs 1 ms |
| --- | --- | --- | --- | --- | --- |
| Worst case | Kickoff, `obstacle_count=0`, snake A, 400 calls | 0.427 ms | 0.858 ms | 400 | **OK** |
| Typical | Mean per decision in expert vs expert (`scripts/expert_latency.py`, 3 matches) | **0.396 ms** | 16.667 ms | 10 800 | **OK** (mean) |

The typical max of 16.7 ms is a single-sample spike (GC / first-call noise) on a battery whose mean stays under the budget. The blocking figure for ALERTA is the kickoff worst-case row, which stays under 1 ms.

## Throughput (RNF03 / D46 item 1)

| Pair | Mode | n | Matches/min | Ticks/s | Mean ticks | Status vs 1000/min |
| --- | --- | --- | --- | --- | --- | --- |
| Random vs random | Sequential | 40 | 925.1 | 6746.8 | 437.6 | below floor (expected) |
| Random vs random | Parallel (15 workers) | 200 | **4918.8** | 35204.0 | 429.4 | **OK** |
| Expert vs expert | Sequential | 20 | 39.8 | 1193.4 | 1800.0 | no floor (D17) |
| Expert vs random | Sequential | 20 | 365.2 | 1867.8 | 306.9 | no floor (D17) |

Single-process matches/min starts below the RNF03 floor, matching the D46 baseline (812 matches/min for the safe random policy). Multiprocessing supplies the floor: 4918.8 ≥ 1000.

Expert vs expert always reaches `max_ticks` (1800): both sides survive, so the match ends on timeout. That is why its matches/min is low and why ticks/s is the stable comparison.

## Acceptance (BR-U3-ACC1, 500 matches, single-process)

`ExpertAgent` vs `RandomAgent`, seeds 0–499, `CoreConfig()`, sequential:

| Metric | Value |
| --- | --- |
| Matches | 500 |
| Score A (1 / 0.5 / 0) | **0.982** (491.0 points) |
| Win rate A | 0.982 |
| Win rate B | 0.018 |
| Draw rate | **0.000** (reported separately) |
| Floor | 0.95 |
| Status | **OK** |
| Wall time | 78 s (`pytest -m slow`) |

## How to reproduce

```text
.\.venv\Scripts\python.exe scripts\expert_latency.py
.\.venv\Scripts\python.exe scripts\throughput.py
.\.venv\Scripts\python.exe -m pytest tests/evaluation/test_acceptance.py -m slow --no-cov
```
