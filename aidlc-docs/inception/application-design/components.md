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
Contrato `act(state) -> Action` para random, expert e human.

## agents.human
Teclas absolutas; buffer FIFO de até **2** comandos; **1** consumido por tick (D28). Ré ignorada (D13).

## agents.tree
`.joblib` + `safety_mask` (D24) usando `is_fatal`. Checa versão scikit-learn (D28).  
`act(state)` devolve **ação executada + ExplanationPayload** (D30): condições do `decision_path`, ação proposta, ação executada, flag de veto. **U7 só traduz (dicionário PT) e renderiza** — não recalcula o caminho da árvore.

## agents.expert / agents.random
Expert usa `flood_fill_count` / `reachable_cells` e `is_fatal` conforme A*.

## config
`config.yaml` via pacote instalado.

## services.match (U3)
`tick` = dois `act` + `engine.step`. Sem relógio. UI e headless definem o ritmo.

## training.* / evaluation.* / ui.*
Como antes; UI não cria `MatchService` — consome o da U3.
