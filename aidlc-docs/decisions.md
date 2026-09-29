# Decisions — Snake vs. Máquina

Decisões da Inception. Fonte: perguntas de requisitos, esclarecimento RF03 e revisões humanas de `requirements.md` em 2026-09-28. **Requisitos aprovados** em 2026-09-28 após D22–D25.

## D01 — Modo de disputa
**Decisão**: Humano e máquina no mesmo tabuleiro 20×20, duas cobras, uma comida.  
**Origem**: requirement-verification-questions Q1=A  
**Status**: Aprovada

## D02 — Painel de explicação
**Decisão**: Painel RF05 sempre visível; tecla para ocultar/mostrar (padrão `H`).  
**Origem**: Q2=C  
**Status**: Aprovada

## D03 — RF08
**Decisão**: Gravação/treino no estilo do jogador fora do MVP.  
**Origem**: Q3=A  
**Status**: Aprovada

## D04 — Escopo das units
**Decisão**: Entregar U1–U5 e U7 completa nesta execução. U6 VIPER no próximo ciclo.  
**Origem**: Q4=X  
**Status**: Aprovada

## D05 — Espectador
**Decisão**: Incluir modo espectador IA vs. IA com Pygame. Prioridade elevada para Should na revisão (ver D20).  
**Origem**: Q5=B  
**Status**: Aprovada; prioridade atualizada em D20

## D06 — Idioma
**Decisão**: Interface em português; identificadores de código em inglês.  
**Origem**: Q6=C  
**Status**: Aprovada

## D07 — Duração vs. velocidade de exibição
**Decisão original (Q7=X)**: 10 ticks/s como padrão, configurável via `config.yaml`; renderização a 60 FPS.  
**Revisão**: O limite da partida é **1800 ticks fixos**, independente de `tick_rate`. `tick_rate` (padrão 10) controla **somente** a velocidade de exibição na UI. Headless avança ticks sem esperar o relógio.  
**Origem**: Q7=X + revisão item 3  
**Status**: Aprovada (revisão)

## D08 — PPO / VIPER
**Decisão**: Não treinar PPO nesta versão.  
**Origem**: Q8=C  
**Status**: Aprovada

## D09 — Security Baseline
**Decisão**: Não aplicar.  
**Origem**: Q9=B  
**Status**: Aprovada

## D10 — Resiliency Baseline
**Decisão**: Não aplicar.  
**Origem**: Q10=B  
**Status**: Aprovada

## D11 — Property-Based Testing
**Decisão**: Aplicação parcial (bloqueantes: PBT-02, PBT-03, PBT-07, PBT-08, PBT-09). Demais consultivos.  
**Origem**: Q11=B  
**Status**: Aprovada

## D12 — Dificuldade Difícil e aceite vs. Médio
**Decisão original**: Difícil = árvore BC profundidade 8 com `safety_mask` ligada. VIPER no próximo ciclo substitui essa configuração se tiver taxa de vitória maior contra o especialista. RF03 permanece Must.  
**Revisão**:
- Aceite de produto do Difícil: taxa de vitória vs. especialista **≥ 10 pontos percentuais acima** do Médio (BC-6, máscara off), mesma bateria de 500 partidas.
- A meta de **≥ 40%** de vitória vs. especialista vale para **BC-8 com máscara ligada**.
- RF05 mostra quando a máscara **vetou** a ação proposta pela árvore.
**Origem**: clarification Q1=X + revisão item 4  
**Status**: Aprovada (revisão)

## D13 — Controle humano absoluto
**Decisão**: O humano usa teclas absolutas (↑/W = cima na tela, etc.). `HumanAgent` converte para ação relativa (`straight`, `turn_left`, `turn_right`) e **ignora marcha à ré** (o pedido oposto à direção atual não muda o curso; segue em frente).  
**Origem**: revisão item 1  
**Status**: Aprovada (revisão)

## D14 — Regras extras de colisão e cauda
**Decisão**:
- (a) Troca de posição das cabeças no mesmo tick = colisão cabeça com cabeça (aplica a regra de tamanho/empate).
- (b) Ambas as cobras morrem no mesmo tick = empate, qualquer causa.
- (c) Entrar na célula que a cauda libera no mesmo tick é permitido, **exceto** se aquela cobra acabou de comer (cauda não libera célula).
**Origem**: revisão item 2  
**Status**: Aprovada (revisão)

## D15 — Veto da máscara no painel
**Decisão**: O painel RF05 indica quando `safety_mask` substituiu a ação da árvore (proposta vs. executada).  
**Origem**: revisão item 4  
**Status**: Aprovada (revisão)

## D16 — Metas de acurácia por modelo
**Decisão**: Acurácia ≥ 95% no conjunto de teste congelado vale para **BC-6 e BC-8**. **BC-3 não tem meta de acurácia**.  
**Origem**: revisão item 5  
**Status**: Aprovada (revisão)

## D17 — Throughput headless
**Decisão**: RNF03 ≥ 1000 partidas/min vale para **random vs. random**. Com o especialista, **medir e registrar** o throughput, sem piso. Multiprocessing permitido.  
**Origem**: revisão item 6  
**Status**: Aprovada (revisão)

## D18 — Rótulos PT das features
**Decisão**: U7 entrega um dicionário de rótulos em português para os nomes de features no painel. Código das features permanece em inglês.  
**Origem**: revisão item 7  
**Status**: Aprovada (revisão)

## D19 — PBT geométrico de features
**Decisão**: Além das invariantes já listadas, `extract_features` deve ser testado por PBT para:
- **Rotação** 90/180/270°: mesmo vetor de features (estado egocêntrico).
- **Espelhamento**: features esquerda ↔ direita trocadas; frente/trás e não-laterais preservados.
**Correção (D38)**: rotação e espelhamento são do **tabuleiro inteiro** em torno do centro / eixos centrais — não em torno da cabeça. Ver D38.
**Origem**: revisão item 8  
**Status**: Aprovada (revisão); geometria corrigida por D38

## D20 — Prioridade RF07
**Decisão**: Modo espectador (RF07) passa de Could para **Should**.  
**Origem**: revisão item 9  
**Status**: Aprovada (revisão)

## D21 — Teste congelado e modelos entregues
**Decisão**: O conjunto de teste do Behavior Cloning é **congelado antes do DAgger** (DAgger só amplia o treino). A grade de `max_depth` 3–12 é **apenas experimental**. Os modelos de produto desta versão são exatamente profundidades **3, 6 e 8**.  
**Origem**: revisão item 9  
**Status**: Aprovada (revisão)

## D22 — Pontuação da taxa de vitória
**Decisão**: Em **todas** as metas de taxa de vitória (vs. aleatório, vs. especialista, D12, U3): vitória = **1**, empate = **0,5**, derrota = **0**. A taxa é a média. A **taxa de empates** (`empates / N`) é reportada **separadamente**.  
**Origem**: revisão 2 item 1  
**Status**: Aprovada

## D23 — Obstáculos internos (U1)
**Decisão**: O núcleo mantém uma lista de células bloqueadas. **Padrão: 0**. Obstáculos são sólidos e entram em features, flood fill, especialista e máscara. Algoritmo de geração: **D26**.  
**Origem**: revisão 2 item 2  
**Status**: Aprovada

## D24 — Semântica da `safety_mask`
**Decisão**: "Morte imediata" = apenas mortes **determinísticas** neste tick: parede, corpos, obstáculos internos, **respeitando D14c** (cauda). Possíveis colisões de cabeça **não** são vetadas. Se vetar: escolher a ação segura com maior `predict_proba`. Se todas forem fatais no sentido determinístico: **manter a ação original** da árvore.  
**Origem**: revisão 2 item 3  
**Status**: Aprovada

## D25 — `space_free_*`, lados e spawns
**Decisão**:
- `space_free_*` = flood fill após o movimento / `min(200, free_cells)`, saturado em `[0, 1]`. **1,0 = espaço suficiente** em qualquer tamanho de mapa.
- Coordenadas (origem canto superior esquerdo, +x direita, +y baixo), tabuleiro 20×20:
  - **NW**: head `(2, 2)`, body `(1, 2)`, `(0, 2)`, direção East `(+1, 0)`
  - **SE**: head `(17, 17)`, body `(18, 17)`, `(19, 17)`, direção West `(-1, 0)`
- Humano vs. máquina: humano NW, máquina SE.
- Torneios e estresse: **alternam** NW/SE a cada partida (índice par: A=NW B=SE; ímpar: A=SE B=NW).
**Origem**: revisão 2 itens 4–5  
**Status**: Aprovada

## D26 — Comida inicial e geração de obstáculos (U1)
**Decisão**:
1. **Comida inicial**: varredura começa em `(10, 9)` (Manhattan 15 a cada cabeça). **Não** usar `(10, 10)` (favorece SE em 2 passos). Primeira célula livre na varredura cíclica `(y, x)` a partir de `(10, 9)`.
2. **Obstáculos**:
   - (a) Zona livre Chebyshev raio 2 ao redor de cada cabeça e da célula à frente (NW `(3, 2)`, SE `(16, 17)`), mais corpos e comida.
   - (b) Simetria rotacional 180°: obstáculo em `(x, y)` implica `(W-1-x, H-1-y)`; `obstacle_count` arredondado **para cima para par**.
   - (c) **D29**: flood fill 4-conectado — **todas** as células livres em um único componente (não só cabeças + comida); senão regenerar com `seed_k = seed + k * 1000003` (até 100 tentativas, depois erro explícito).
**Origem**: fechamento Inception, design U1  
**Status**: Aprovada

## D27 — Ordem de construction, alerta D12 na U5, NFR por unit
**Decisão**:
1. Ordem: **U1 → U2 → U3 → U5 → U4 → U7**. U5 antes da UI porque é o maior risco (acurácia, D12) e não depende da U4.
2. Aceite da U5 inclui **checagem antecipada de D12**: 100 partidas BC-8 (máscara on) e BC-6 vs. especialista; reportar a diferença de taxa (1/0,5/0). **Alerta apenas** — não substitui as 500 partidas da U7.
3. **NFR Requirements e NFR Design** só em **U1, U2, U3, U4**. **Pular** em U5 e U7 (métricas já em requirements.md).
4. No diagrama do execution plan, Code Generation e Build and Test ficam **laranja (pendentes)**, não verde.
**Origem**: aprovação do execution plan  
**Status**: Aprovada

## D28 — Cortes de Application Design (Q1–Q4 humanas)
**Decisão**:
1. Core = `state`, `engine` (só tick), `features`, **`setup.py`** (spawns, comida inicial, obstáculos D26).
2. Q2 = A: `MatchService` criado na **U3** (não na U4). `step`/`tick` avançam um tick e **não** conhecem relógio; UI e headless controlam o ritmo. `HumanAgent`: buffer de até **2** comandos, consome **1** por tick.
3. `safety_mask` permanece em `agents.tree`. Core expõe `is_fatal(state, snake_id, action)` e `flood_fill(state, start, limit=200)` para máscara, especialista e features. PBT: se `is_fatal` é False, o tick simulado não mata a cobra por causa determinística.
4. Layout `src/snake_vs_machine/{core,agents,training,evaluation,ui}` com `pyproject.toml` e `pip install -e .`.
5. Versão do scikit-learn **pinada** no `pyproject.toml` e no JSON de cada modelo; incompatibilidade cai no **erro 4** (junto com `.joblib` ausente).
**Origem**: revisão Application Design  
**Status**: Aprovada (com D29)

## D29 — Conectividade total e cauda em `is_fatal`
**Decisão**:
1. **D26c**: a checagem de conectividade exige que **todas** as células livres formem um único componente 4-conectado (não só cabeças + comida), porque a comida renasce em qualquer livre e pode cair num bolsão inalcançável.
2. **`is_fatal`** (docstring + teste unitário obrigatório):
   - Célula que a **cauda do oponente** libera: convenção **conservadora** — **sólida** se a cabeça do oponente estiver **adjacente à comida** (4-vizinhos; pode comer neste tick); **livre** caso contrário.
   - **Própria cauda**: usar o resultado **real** da própria ação (come → cauda não libera; senão libera).
   - Caso de teste: oponente adjacente à comida.
**Origem**: aprovação Application Design  
**Status**: Aprovada

## D30 — Aceite das units, DoD e seta U5–U4
**Decisão**:
1. **U1**: cobertura `core/` ≥ 80%; PBT `is_fatal` (False ⇒ tick não mata por causa determinística); PBT `setup` (simetria 180°, todas as livres conectadas, zonas livres, determinismo por seed).
2. **U3**: RNF03 ≥ 1000 partidas/min random vs. random; registrar throughput vs. especialista.
3. **U5**: BC-8 ≥ 90% vs. aleatório; inferência < 1 ms/jogada **com** `safety_mask` (esclarecido em **D40**: inclui `extract_features` + `predict_proba` + `safety_mask`). `TreeAgent` devolve ação **e** dados de explicação (`decision_path`, ação proposta, ação executada, flag de veto). **U7 só traduz e renderiza**.
4. **U7**: BC-8 com máscara ≥ 40% vs. especialista; queda ≤ 15 pp com 10% de ruído; relatório com **todas** as metas da tabela Metrics (aprovado/reprovado).
5. **DoD** de toda unit: `ruff` limpo, `pytest` verde, type hints nas funções públicas, `decisions.md` atualizado, **commit + tag git `uN-done`**.
6. Diagrama: seta **U5 → U4 tracejada** (ordem de risco, não dependência de compilação).
**Origem**: aprovação Units  
**Status**: Aprovada

## D31 — Núcleo U1 (respawn, H2H+comida, State, PBT, cobertura)
**Decisão**:
1. **Comida no meio da partida**: sorteio uniforme entre células livres. RNG puro `numpy.random.default_rng(SeedSequence([match_seed, tick]))`. Proibido `hash()` do Python. Stream **separado** da geração de obstáculos. Comida inicial continua D26 (varredura `(10,9)`).
2. **Duas cabeças na comida**: resolver cabeça-com-cabeça primeiro (regra 4). Sobrevivente come e cresce; se ambas morrem, a comida permanece.
3. **`engine.step` é puro** (devolve `State` novo; entrada intacta). `death_cause` por cobra ∈ `{wall, obstacle, self_body, opponent_body, head_to_head}` (`None` se viva). Timeout **não** é causa de morte: `end_reason` ∈ `{death, timeout}` (`None` enquanto a partida corre). Morte simultânea: registrar a causa de **cada** cobra.
4. **PBT `is_fatal` False**: para as **três** ações do oponente, `step` não mata a cobra testada por parede, obstáculo ou corpo. Mortes `head_to_head` (e a célula da cabeça pré-tick do oponente, D24) não violam a propriedade.
5. **1000 partidas**: helper de teste (não `RandomAgent`); cobertura ≥ 80% de `core/{state,setup,engine,queries}` na U1; após U2 a mesma meta vale para todo `core/` incluindo `features.py`.
**Origem**: respostas Functional Design U1  
**Status**: Aprovada (P-FATAL e cabeça do oponente emendados pela D32)

## D32 — Cabeça do oponente, occupancy compartilhada e flood_fill
**Decisão**:
1. Entrar na cabeça pré-tick do oponente é **cabeça com cabeça só na troca** (`next_a == head_b` e `next_b == head_a`). Sem troca, a célula vira pescoço → `death_cause = opponent_body`. Teste obrigatório: A `(5,5)` E, B `(6,5)` N, ambos `straight` → A morre `opponent_body`; B vive.
2. `is_fatal`: cabeça atual do oponente é **FATAL** (conservador: no motor, só sobrevive na troca se for o maior). Emenda D24 neste ponto. Encontro no mesmo `next` (célula terceira) continua H2H, não é `is_fatal`.
3. **P-FATAL**: sem exceção de célula; vale para **todas** as células. `head_to_head` (mesmo `next` ou troca) não viola.
4. **P-ENG-NOOVERLAP**: após qualquer `step`, células de cobras **vivas** são todas distintas (entre cobras e dentro da mesma).
5. `next_occupancy(state, snake_id, action)` em `core.queries`: corpos com caudas que liberam removidas (própria cauda pela ação real; oponente D29). `engine.step` **usa** essa função no passo 5. `flood_fill_*` aceita `occupancy` opcional. PBT: `step` e `next_occupancy` concordam nas células ocupadas após o tick, **excluindo as cabeças novas**.
6. Assinaturas: `flood_fill_count(...) -> int` e `reachable_cells(...) -> frozenset[Cell]`. Sem `flood_fill` único.
7. Passo 6: se **só um** dos dois é candidato a H2H, **esse sobrevive** (não aplica regra de tamanho).
**Origem**: revisão Functional Design U1  
**Status**: Aprovada (cauda do oponente no `step` emendada pela D33)

## D33 — `next_occupancy` real vs conservador
**Decisão**:
1. `next_occupancy(state, snake_id, action, opponent_action=None)`:
   - `opponent_action` informado → cauda do oponente sólida **só** se `next_head` do oponente == food.
   - `opponent_action is None` → D29 (sólida se a cabeça do oponente estiver 4-adjacente à comida).
2. `engine.step` passo 5 chama com a ação **real** do oponente. `is_fatal`, features (U2) e especialista (U3) chamam **sem** `opponent_action`.
3. Teste obrigatório: cabeça de B adjacente à comida, B vira e não come; A entra na cauda que B libera → A **sobrevive**.
4. **P-OCC-CONSERV**: `next_occupancy(s, id, a) ⊇ next_occupancy(s, id, a, opponent_action)` para toda ação do oponente.
**Origem**: aprovação Functional Design U1  
**Status**: Aprovada

## D34 — NFR U1 (numpy pin, Hypothesis, tipos, cobertura, bench)
**Decisão**:
1. **numpy** pinado no `pyproject.toml` (NEP 19: `Generator.choice` / `shuffle` sem estabilidade entre versões). A mesma versão entra no JSON dos modelos (U5) e nos relatórios (U7), junto com a do scikit-learn.
2. **Hypothesis**: perfil `dev` (100 exemplos, `deadline=None`) e `full` (1000 exemplos, `deadline=None`), escolhidos por variável de ambiente. Rodar `full` antes da tag `u1-done`. `.hypothesis/` no `.gitignore`.
3. **Tipos**: `State` e `Snake` = `@dataclass(frozen=True, slots=True)`; `Cell` = `NamedTuple(x, y)`; `body` = `tuple[Cell, ...]`; `obstacles` e occupancy = `frozenset[Cell]`.
4. Cobertura com `--cov-branch`; a meta ≥ 80% vale para **ramos**.
5. Benchmark **informativo** (não é gate): tempo médio por `step` e partidas/min do helper aleatório em `aidlc-docs/construction/u1-core/benchmark.md`, com descrição da máquina.
6. **Opcional**: `mypy --strict` em `core/`.
**Origem**: aprovação NFR Requirements U1  
**Status**: Aprovada

## D35 — State sem mapas mutáveis; hash estável
**Decisão**:
1. `State` **não** guarda `dict` de cobras/lados. Campos fixos `snake_a` / `snake_b` e `side_a` / `side_b` (ou `tuple` indexada por `SnakeId`) mais acessor `snake(id)`.
2. Nenhum `dict`, `list` ou `set` mutável **dentro** de `State`, `Snake` ou `CoreConfig`.
3. Teste obrigatório: `hash(state)` funciona; atribuir qualquer campo levanta `FrozenInstanceError`.
4. Sugestão (não requisito): helper `_body_cells(state)` calculado uma vez por `step` e reusado nas duas chamadas de `next_occupancy`.
**Origem**: aprovação NFR Design U1  
**Status**: Aprovada

## D36 — Code Generation Plan U1 (TDD, PBT por construção, replay)
**Decisão**:
1. Antes do `engine`, escrever testes críticos a partir de `business-rules.md` (D32 ram, troca, D33 cauda com/sem comer, H2H na comida, morte simultânea), rodá-los e mostrar a falha; só então implementar `engine`.
2. PBT gera estados por `new_match` + `step` (seed, `obstacle_count`, sequência de ações do Hypothesis). Sem `State` arbitrário montado à mão.
3. Mesma seed + mesma sequência de ações → partidas idênticas estado a estado (inclui respawn de comida).
4. `pyproject.toml`: distribuição `snake-vs-machine`, import `snake_vs_machine`; `fail_under = 80` com branch coverage.
**Origem**: aprovação Code Generation Plan U1  
**Status**: Aprovada

## D37 — Python mínimo 3.13
**Decisão**: `requires-python = ">=3.13"`; Ruff `target-version = "py313"`; mypy `python_version = "3.13"`. A suíte U1 (incluindo `HYPOTHESIS_PROFILE=full` pelo revisor) rodou neste runtime 3.13; não se mantém a promessa de 3.11.
**Origem**: aprovação Code Generation U1 (opção b)  
**Status**: Aprovada

## D38 — Features U2 (geometria PBT, consistência, schema, ValueError)
**Decisão**:
1. **Geometria (corrige D19)**: rotação 90/180/270° em torno do **centro do tabuleiro** (tabuleiro quadrado). Espelhamento do **tabuleiro inteiro** no eixo central: `x → W−1−x` **ou** `y → H−1−y`. Ambas as transformações aplicam-se a corpos, direções, comida e obstáculos — não em torno da cabeça.
2. **Consistência PBT**: para `d ∈ {ahead, left, right}`: `danger_d = 1 ⇔ dist_danger_d = 0`; `danger_d = 1 ⇒ space_free_d = 0`.
3. `FEATURE_SCHEMA_VERSION: int` em `core.features` junto de `feature_names()`. U5 grava a versão no JSON de cada modelo; `TreeAgent` recusa modelo com versão diferente (erro 4).
4. `extract_features` lança `ValueError` se a cobra estiver morta **ou** a partida for terminal. Geradores PBT filtram esses estados.
5. Respostas FD U2: Q1=A (`danger_*` = `is_fatal`); Q2=X (raio a partir da célula de destino; bloqueio = mesmo conjunto de `is_fatal` / `next_occupancy` conservador daquela ação; divisor `max(width, height)`); Q3=A; Q4=A; Q5=B (semiplanos inclusivos; `food is None` ou comida na cabeça → quatro bits 0); Q6=A; Q7=B (landing ∈ 3 next heads do oponente); Q8=A (`tuple` de 20 + `feature_names` + versão); Q9=B.
**Origem**: Functional Design U2  
**Status**: Aprovada (respostas + registro explícito)

## D39 — Features U2 (flood count, golden vector, justiça)
**Decisão**:
1. `flood_fill_count` devolve **exatamente** `min(células alcançáveis, limit)`, independente da ordem de visita. Features usam **só** a contagem. `reachable_cells` com `limit` depende da ordem da BFS e **não** alimenta features. Teste na U1: em estados gerados, a contagem é igual após rotação/espelhamento do tabuleiro.
2. Teste **golden vector** obrigatório: `new_match(CoreConfig(), seed=0)` (0 obstáculos), cobra A, vetor  
   `(0, 0, 0, 0.85, 0.10, 0.85, 1.0, 1.0, 1.0, 1, 0, 1, 0, 15/38, 0, 30/38, 0, 0, 0, 0)`  
   com `pytest.approx` nos floats.
3. Teste de justiça: no mesmo kickoff, `extract_features(state, A) == extract_features(state, B)`.
4. O exemplo 1 da lista de worked examples do FD U2 é **substituído** pelos itens 2 e 3.
**Origem**: aprovação Functional Design U2  
**Status**: Aprovada

## D40 — Orçamento de inferência (U2 + U5)
**Decisão**:
1. O aceite U5 **inferência < 1 ms/jogada com máscara** mede o caminho completo: `extract_features` + `predict_proba` + `safety_mask`.
2. Orçamento U2: `extract_features` ≤ **0,5 ms** por chamada no pior caso (kickoff, 0 obstáculos, três flood fills no limite 200). **Informativo**: gravar em `benchmark.md`; se exceder, marcar **ALERTA** — **não** falha o pytest.
3. Se houver alerta, anotar otimização futura (não implementar na U2): quando os três destinos compartilham a mesma região com ≥ 200 células, um único `flood_fill_count` serve as três direções.
**Origem**: aprovação NFR Requirements U2  
**Status**: Aprovada

## D41 — Code Generation Plan U2 (helpers + commit D39)
**Decisão**:
1. Antes das propriedades PBT, testar helpers de transformação: `rot90` quatro vezes = identidade; cada espelho duas vezes = identidade; `rot180` do kickoff leva o corpo de A ao spawn de B e vice-versa.
2. Antes da Etapa 1 da U2, commit separado das mudanças U1 da D39 (`flood_fill_count` + isometria).
**Origem**: aprovação Code Generation Plan U2  
**Status**: Aprovada

## D42 — `free_cells` aritmético em `extract_features`
**Nota de numeração**: pedida como "D41" na revisão do código da U2, mas D41 já estava ocupada pelo plano de CG da U2. Registrada como **D42**.
**Decisão**:
1. `free_cells` é calculado **uma vez** por chamada de `extract_features`, fora do laço das ações, por `width*height - len(obstacles) - len(me.body) - len(opp.body)` (válido por P-ENG-NOOVERLAP e porque cobra viva nunca ocupa obstáculo). `_space` recebe `free_cells` como parâmetro.
2. Nova propriedade PBT: a fórmula é igual à contagem célula a célula (oráculo só no teste).
3. `danger` continua sendo `is_fatal`. Registrar o bench do pior caso antes e depois do item 1.
**Medição**: pior caso kickoff — **4,11 ms antes**, **2,12 ms depois**. Continua **ALERTA** frente ao orçamento de 0,5 ms (D40).
**Origem**: revisão do código U2  
**Status**: Aprovada

## D43 — Otimizar `extract_features` até ≤ 0,5 ms em passos medidos
**Decisão**: otimizar em passos, medindo depois de cada um e parando ao atingir a meta.
1. `reachable_cells` (U1): BFS interno com índices inteiros (`y*width + x`) e grade de bloqueio pré-calculada (lista de bool), sem criar `Cell` por vizinho nem chamar `in_bounds` por célula. Assinatura e retorno públicos inalterados; isometria da D39 preservada.
2. `features`: `danger` derivado de `_blocked(state, landing, occ)`, sem `is_fatal` no laço. Nova propriedade PBT: para toda ação, esse `danger == is_fatal(state, id, action)`.
3. Só se ainda > 0,5 ms: flood compartilhado da D40.
**Resultado**: passo 1 → 0,543 ms (ALERTA); passo 2 → **0,415 ms (OK)**. Passo 3 **não implementado** — meta atingida. Cumulativo 4,11 ms → 0,415 ms.
**Origem**: revisão do código U2 (Solicitar Alterações)  
**Status**: Aprovada
