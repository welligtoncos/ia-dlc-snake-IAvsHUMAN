# Application Design — Snake vs. Máquina

Consolidado após **D28**, **D29** e **D30**. Application Design **aprovado**. Units **aprovadas** (Inception encerrada).

## Style
Python 3.11+; pacote `src/snake_vs_machine/{core,agents,training,evaluation,ui}`; `pyproject.toml`; `pip install -e .`.  
`Agent.act(state, snake_id) -> Action` (todos os agentes). `TreeAgent.decide(state, snake_id)` devolve `ActResult` = **ação + ExplanationPayload** (D30/D45); U7 só traduz e renderiza. Núcleo puro.

## Core split (Q1 revisada)
- `state` — dados
- `setup` — spawns, comida inicial, obstáculos D26 (`setup.py`)
- `engine` — **somente** regras do tick (`step` sem relógio)
- `features` — vetor (U2)
- `queries` — `next_occupancy`, `is_fatal`, `flood_fill_count`, `reachable_cells` (U1, D32)

## Tick (Q2 = A + ritmo)
`MatchService` na **U3**. `step`/`tick` não conhecem relógio. UI e headless controlam o ritmo.  
`HumanAgent`: buffer de até 2 comandos absolutos; consome 1 por tick.

## safety_mask (Q3 revisada)
Política da máscara em `agents.tree`. Núcleo expõe `next_occupancy`, `is_fatal`, `flood_fill_count`, `reachable_cells`.  
PBT: `is_fatal is False` ⇒ tick simulado não mata por causa determinística em **qualquer** célula (D32). Cabeça do oponente é fatal em `is_fatal`. Cauda: D29.

## Layout (Q4 revisada)
Não usar `src/core` solto. Usar `src/snake_vs_machine/...` + instalação editável.

## scikit-learn (item 5)
Versão **pinada** no `pyproject.toml` e gravada no JSON de cada modelo. Incompatibilidade = **erro 4** (com arquivo ausente).

## Units mapping (D27 + D28)

| Unit | Components | NFR |
| --- | --- | --- |
| U1 | state, setup, engine, queries (`next_occupancy`, `is_fatal`, `flood_fill_*`) | Yes |
| U2 | features (usa `flood_fill_count` / `reachable_cells`) | Yes |
| U3 | agents.base, random, expert, human (buffer), **MatchService** | Yes |
| U5 | tree (máscara + sklearn pin + ExplanationPayload), training.*, alerta D12 100 | No |
| U4 | ui.* (ritmo visual; consome MatchService) | Yes |
| U7 | labels PT, torneio 500, stress | No |
| U6 | — | Out |

## Out of this version
Gymnasium, PPO, VIPER, RF08, cloud infra.
