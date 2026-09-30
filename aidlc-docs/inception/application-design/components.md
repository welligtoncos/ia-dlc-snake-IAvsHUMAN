# Components — Snake vs. Máquina

Pacote `snake_vs_machine` em `src/snake_vs_machine/`. Núcleo sem Pygame. **D28**.

## core.state
**Purpose**: Dados da partida (tabuleiro, cobras, comida, obstáculos, tick, seed).  
**Responsibilities**: Tipo `State`; cópia/snapshot. **Não** monta partida nova (isso é `core.setup`).

## core.setup
**Purpose**: Spawns NW/SE (D25), comida inicial (D26), geração de obstáculos (D26).  
**Responsibilities**: `new_match(...)`. Engine não gera obstáculos nem escolhe comida.

## core.engine
**Purpose**: Só as **regras do tick**.  
**Responsibilities**: `step(state, action_a, action_b)` — movimento simultâneo, colisões, cauda, 1800 ticks, outcome. Passo 5 usa `next_occupancy(..., opponent_action=real)` (D33). Sem relógio, sem Pygame, sem `safety_mask`, sem spawn.

## core.queries
**Purpose**: Funções puras compartilhadas.  
**Responsibilities**: `next_occupancy`, `is_fatal`, `flood_fill_count`, `reachable_cells`.  
`is_fatal`: parede, obstáculos, occupancy (D29). **Cabeça atual do oponente é FATAL** (D32; conservador vs. troca com o maior). Encontro no mesmo `next` (célula terceira) não é `is_fatal`.

## core.features
**Purpose**: Vetor de 20 features. Usa `flood_fill_count` / `reachable_cells` de `core.queries`.

## agents.base
Contrato `Agent.act(state, snake_id) -> Action` para random, expert, human e tree (D44/D45).  
Protocolo opcional `ExplainingAgent.decide(state, snake_id) -> ActResult`, implementado só pelo `TreeAgent`.

## agents.human
Teclas absolutas; buffer FIFO de até **2** comandos; **1** consumido por tick (D28). Ré e comandos redundantes filtrados no `push_absolute` (D44); com o buffer cheio, a tecla nova é **ignorada** (D45).

## agents.tree
`.joblib` + `safety_mask` (D24) usando `is_fatal`. `from_joblib` checa as versões de **scikit-learn** e **numpy** e o `FEATURE_SCHEMA_VERSION` (D28/D45).  
`decide(state, snake_id)` devolve `ActResult` = **ação executada + ExplanationPayload** (D30): condições do `decision_path`, ação proposta, ação executada, flag de veto. O payload trafega pelo `on_tick` do `MatchService`; nada é guardado no agente (D45). **U7 só traduz (dicionário PT) e renderiza** — não recalcula o caminho da árvore.

## agents.expert / agents.random
Expert **sem A\*** (D44): distância BFS do destino até a comida + `flood_fill_count` + `is_fatal`, com ordem de decisão total.

## config
`config.yaml` via pacote instalado.

## services.match (U3)
Pacote `services/` acrescentado pela **D44** (fora da lista original da D28): depende de `core` e `agents`; consumido por `ui`, `training` e `evaluation`.  
`tick` = dois `act` + `engine.step`. Sem relógio. UI e headless definem o ritmo. Medição de latência fica no `TimedAgent` de `evaluation` (U7, D44).

## training.* / evaluation.* / ui.*
Como antes; UI não cria `MatchService` — consome o da U3.
