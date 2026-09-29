# U1 Core — NFR Design Plan

**Unit**: `u1-core`  
**Prerequisite**: NFR Requirements approved (D34)

## Execution checkboxes

- [x] Read U1 NFR requirements and D34
- [x] Evaluate resilience / scale / security / logical-infra categories (all N/A or in-process — see below)
- [x] No new [Answer] questions — D34 closed the remaining NFR choices
- [x] Write `nfr-design-patterns.md`
- [x] Write `logical-components.md`
- [x] Present two-option NFR Design completion (next: U1 Code Generation; Infrastructure Design skipped per D27)

## Category evaluation (no questions)

| Category | Status | Evidence |
| --- | --- | --- |
| Resilience | N/A | D10 off; local pure functions; `SetupError` is fail-fast only |
| Scalability | N/A | Single-process library; no cluster, queue, or cache |
| Performance | Locked D34 | Informative bench; flood-fill 200; no clock in `step` |
| Security | N/A | D09 off; no network, no secrets in U1 |
| Logical infra | N/A | No queues, brokers, or circuit breakers |

## Questions

None.
