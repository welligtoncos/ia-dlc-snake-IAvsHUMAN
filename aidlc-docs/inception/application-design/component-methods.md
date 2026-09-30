# Component Methods — Snake vs. Máquina

## core.state

| Method | In | Out | Purpose |
| --- | --- | --- | --- |
| `copy(state)` | `State` | `State` | Deep snapshot; alias-free (D31/PBT-02) |

## core.setup

| Method | In | Out | Purpose |
| --- | --- | --- | --- |
| `new_match(config, seed, sides)` | config, seed, NW/SE | `State` | Spawns D25, comida `(10,9)`, obstáculos D26 |

## core.engine

| Method | In | Out | Purpose |
| --- | --- | --- | --- |
| `step(state, action_a, action_b)` | estado + 2 ações | `State` | Tick puro (não muta a entrada); `death_cause` / `end_reason` (D31) |
| `is_terminal(state)` | `State` | `bool` | `end_reason is not None` |
| `outcome(state)` | `State` | win A / win B / draw | D14b; timeout por tamanho; empate se ambas morreram |

## core.queries

| Method | In | Out | Purpose |
| --- | --- | --- | --- |
| `next_occupancy(state, snake_id, action, opponent_action=None)` | estado, id, ações | `frozenset[Cell]` | Cauda própria real; oponente real se `opponent_action` set, senão D29 (D33) |
| `is_fatal(state, snake_id, action)` | estado, id, ação | `bool` | OOB, obstáculo, ou `next` ∈ occupancy **conservadora**. Cabeça oponente FATAL (D32) |
| `flood_fill_count(state, start, occupancy=None, limit=200)` | estado, célula, occupancy, teto | `int` | Alcance 4-conectado |
| `reachable_cells(state, start, occupancy=None, limit=200)` | estado, célula, occupancy, teto | `frozenset[Cell]` | Mesmo walk; conjunto |

PBT (D32/D33): se `is_fatal` é False, `step` contra as **três** ações do oponente não mata por parede, obstáculo ou corpo em **qualquer** célula. `head_to_head` não viola.  
P-OCC: leftover `body[1:]` = occupancy **com** `opponent_action` real ∩ corpo pré-tick.  
P-OCC-CONSERV: occupancy sem oponente ⊇ occupancy com oponente.  
U1: testes D32 `(5,5)/(6,5)` e D33 (B adjacente à comida, vira, A pisa a cauda e vive).

## core.features

| Method | In | Out | Purpose |
| --- | --- | --- | --- |
| `extract_features(state, snake_id)` | estado, id | `FeatureVector` | Usa `flood_fill_count` / `reachable_cells`; `space_free` / min(200, livres) |
| `feature_names()` | — | `tuple[str, ...]` | Nomes em inglês (D45) |
| `FEATURE_SCHEMA_VERSION` | — | `int` | Versão do esquema; gravada pela U5 e conferida no carregamento (D38) |

## agents.base

| Method | In | Out | Purpose |
| --- | --- | --- | --- |
| `Agent.act(state, snake_id)` | estado, id | `Action` | Contrato de todos os agentes (`typing.Protocol`, D44/D45) |
| `ExplainingAgent.decide(state, snake_id)` | estado, id | `ActResult` | Protocolo opcional; só o `TreeAgent`. `ActResult` = ação executada + `ExplanationPayload` (D45) |

## agents.human

| Method | In | Out | Purpose |
| --- | --- | --- | --- |
| `push_absolute(direction)` | direção absoluta | — | Enfileira; cap 2 (FIFO). Buffer cheio: **ignora a tecla nova** (D45) |
| `act(state, snake_id)` | estado, id | `Action` | Consome **1** comando; se vazio, `straight`; converte. Ré e comandos redundantes são filtrados no `push_absolute` (D44) |

## agents.tree

| Method | In | Out | Purpose |
| --- | --- | --- | --- |
| `from_joblib(path, safety_mask)` | arquivo, flag | `TreeAgent` | `ModelLoadError(reason=missing\|sklearn\|numpy\|schema)` se o arquivo faltar ou as versões divergirem do JSON (D45/D50) |
| `decide(state, snake_id)` | estado, id | `ActResult` | predict; máscara via `is_fatal` + maior `predict_proba` segura (empate: `straight`, senão stream dos agentes); `TreeExplanation` com `proba` e `path` (D50) |
| `act(state, snake_id)` | estado, id | `Action` | `decide(...).action`; conformidade com o protocolo `Agent` |

Sem `explain(state)`: a explicação chega à U7 pelo `ActResult` do `decide`, repassado no `on_tick`. Nenhum agente guarda a última explicação em estado (D45).

## services.match (entregue na U3)

| Method | In | Out | Purpose |
| --- | --- | --- | --- |
| `tick(state, agent_a, agent_b)` | estado + 2 agentes | `State` | `decide` se o agente o implementa, senão `act`; + `engine.step`; **não** dorme, **não** lê relógio (D45) |
| `play(agent_a, agent_b, config, seed, sides, on_tick=None)` | agentes, config, seed, lados, hook | `MatchResult` | Loop de `tick` até terminal; ritmo = o do caller; `on_tick` recebe `(antes, ActResult A, ActResult B, depois)` (D44/D45) |

## Demais métodos
`training.*`, `evaluation.*`, `ui.*` como no design anterior; `ui` chama `MatchService.tick` no ritmo de `tick_rate` / 60 FPS; headless chama `tick`/`play` sem espera.
