# U3 Agents + MatchService — NFR Design Plan

**Unit**: `u3-agents`
**Prerequisite**: NFR Requirements approved (D46, including Q8=A)

## Execution checkboxes

- [x] Read `u3-agents/nfr-requirements/{nfr-requirements,tech-stack-decisions}.md`
- [x] Map each NFR to a pattern or a logical component
- [x] Collect answers in this file (`[Answer]:` tags)
- [x] Resolve ambiguities — Q3 and Q4 X answers were fully specified; registered as D48
- [x] Write `aidlc-docs/construction/u3-agents/nfr-design/nfr-design-patterns.md`
- [x] Write `aidlc-docs/construction/u3-agents/nfr-design/logical-components.md`
- [x] Propagate the D48 consequence: `MatchResult` drops `score_a`; scoring owned by `evaluation/scoring.py`
- [x] Present two-option NFR Design completion (next: U3 Code Generation)

No application code in this stage.

## Category assessment (rule requires all categories to be judged)

| Category | Applicable | Justification |
| --- | --- | --- |
| Performance patterns | **Yes** | RNF03 floor, expert ≤ 1 ms, lazy RNG, single BFS from the food |
| Scalability patterns | **Yes, narrowly** | Only batch parallelism for throughput (D46 item 1). No load growth, no service scaling |
| Resilience patterns | **Minimal** | Resiliency Baseline disabled (D10). Fail-fast only: `TypeError` / `ValueError`, no retries, no fallbacks |
| Security patterns | **No** | Security Baseline disabled (D09). No network, no persistence, no untrusted input; agents are in-process code |
| Logical components | **Yes** | Agent protocols, expert internals, `services.match`, the `scripts/` layer and the worker function for multiprocessing |
| Availability / DR | **No** | Desktop, in-process, no uptime target |
| Observability | **Minimal** | No logging framework; measurement flows through `scripts/` into `benchmark.md` |

## Decided, not re-asked

| Item | Source |
| --- | --- |
| RNF03 floor from the multiprocess run; single-process and ticks/s also reported | D46 item 1 |
| Expert ≤ 1 ms per decision, ALERTA only | D46 item 2 |
| One BFS from the food per decision, proven exact | D46 item 3 |
| Coverage 80% branch over `core` + `agents` + `services`; mypy strict on all three | D46 items 4–5 |
| `TypeError` naming agent and side on contract violation | D46 item 6 |
| Generated `CoreConfig` with `max_ticks` ≈ 60 for properties | D46 item 7 |
| Lazy RNG construction | D46 item 8 |
| 95% battery as a `slow` pytest test; measurement scripts in `scripts/` | D46 item 9 |

---

# Questions

## Question 1
How should the multiprocessing throughput run be shaped? Note that Windows uses the `spawn` start method, so the worker has to be an importable module-level function and every argument must pickle.

A) `multiprocessing.Pool.imap_unordered` over a range of seeds, chunked, with `processes = os.cpu_count() - 1`; the worker plays one match and returns a small `MatchResult`

B) `concurrent.futures.ProcessPoolExecutor` with the same shape, for a friendlier API and easier cancellation

C) A worker that plays a **batch** of seeds and returns aggregated counts, to cut per-task pickling overhead

X) Other (please describe after [Answer]: tag below)

[Answer]: A — com chunksize explícito, e os agentes construídos DENTRO do worker a partir de uma especificação simples (nome + parâmetros), nunca enviados como objetos. Os resultados chegam fora de ordem: agregação independente da ordem e, para qualquer comparação, ordenar por seed.

## Question 2
Where does the lazy tick-RNG helper live, given that both `RandomAgent` and `ExpertAgent` need the same stream definition?

A) A shared private helper in `agents/base.py` (e.g. `_tick_rng(state, snake_id)`), imported by both agents

B) Duplicated privately in each agent module, keeping `base.py` limited to protocol definitions

C) In `core/` next to the other `SeedSequence` streams, so every stream tag lives in one place

X) Other (please describe after [Answer]: tag below)

[Answer]: C — um módulo core/rng.py com todas as tags de stream (0, tick, 2_000_003, 3_000_003) e o helper genérico; os agentes importam dele.

## Question 3
Should the `slow` 500-match acceptance test also use multiprocessing?

A) No — keep it single-process and simple; it is a `slow` test and correctness does not depend on speed

B) Yes — reuse the same worker as the throughput script, so the acceptance test doubles as a check that the parallel path produces identical results

C) Single-process by default, with an opt-in environment variable to run it in parallel locally

X) Other (please describe after [Answer]: tag below)

[Answer]: X — O teste slow de 500 partidas fica single-process (opção A). Separadamente, um teste rápido joga ~20 seeds em modo sequencial e em paralelo e verifica que os MatchResult são idênticos.

## Question 4
The expert's 1 ms budget needs a defined worst case, the way U2 fixed "kickoff, no obstacles, three floods at 200".

A) Kickoff, `obstacle_count=0`, snake A — the same scenario as U2, so the two benchmarks are comparable

B) A mid-match state with obstacles and long bodies, where the BFS from the food traverses more of the board

C) Both, recorded as separate rows in `benchmark.md`

X) Other (please describe after [Answer]: tag below)

[Answer]: X — Duas linhas: o kickoff sem obstáculos (pior caso, comparável à U2) e a média por decisão ao longo de partidas reais especialista vs. especialista (o número que determina o tempo das baterias da U7)

## Question 5
How should `MatchResult` aggregation for the batteries be designed, given that U7 will later run tournaments over the same primitive?

A) U3 ships only `play` returning one `MatchResult`; aggregation (win rate, draw rate, throughput) lives in the `scripts/` layer and is re-implemented properly in U7

B) U3 ships a small `aggregate(results) -> Summary` helper in `services/match.py`, reused by the scripts now and by U7 later

C) U3 ships the helper in `evaluation/` instead, claiming a bit of U7 territory early to avoid duplication

X) Other (please describe after [Answer]: tag below)

[Answer]: C — evaluation/scoring.py mínimo agora (pontuação 1/0,5/0, taxa de vitória, taxa de empates); a U7 estende com intervalo de confiança e relatórios.
