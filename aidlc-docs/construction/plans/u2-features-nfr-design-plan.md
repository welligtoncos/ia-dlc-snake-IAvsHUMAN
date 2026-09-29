# U2 Features — NFR Design Plan

**Unit**: `u2-features`  
**Prerequisite**: NFR Requirements approved (D40)

## Execution checkboxes

- [x] Read U2 NFR requirements and D38–D40
- [x] Evaluate resilience / scale / security / logical-infra (N/A — same as U1)
- [x] No new [Answer] questions — D40 closed latency and ALERTA policy
- [x] Write `nfr-design-patterns.md`
- [x] Write `logical-components.md`
- [x] Present two-option NFR Design completion (next: U2 Code Generation; Infrastructure Design skipped per D27)

## Category evaluation (no questions)

| Category | Status | Evidence |
| --- | --- | --- |
| Resilience | N/A | D10 off; `ValueError` is fail-fast only |
| Scalability | N/A | In-process function; no queue or cache |
| Performance | Locked D40 | ≤ 0.5 ms informative; ALERTA; shared-flood deferred |
| Security | N/A | D09 off; no I/O |
| Logical infra | N/A | No brokers or circuit breakers |

## Questions

None.
