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

## D44 — Functional Design da U3 (agentes + MatchService)
**Respostas**: Q1=B, Q2=B, Q3=X, Q4=X, Q5=A, Q6=X, Q7=X, Q8=C, Q9=A, Q10=A, Q11=A, Q12=A.
**Decisão**:
1. **Especialista sem A\***: para cada uma das três ações, distância BFS do destino até a comida (ocupação conservadora + obstáculos). Ordem de decisão:
   (1) descartar fatais; (2) descartar risco de cabeça (destino ∈ próximas cabeças possíveis do oponente) salvo se estritamente maior; (3) descartar as que falham `flood_fill_count(destino, occ, 200) > len(body)`;
   (4) menor distância à comida → maior flood → `straight`; (5) empate esquerda/direita: sorteio com o RNG do tick;
   (6) fallbacks: se 2 ou 3 eliminar tudo, voltar ao conjunto anterior e escolher o maior flood; se todas fatais, `straight`.
   Complemento (Q4): as possíveis próximas cabeças do oponente só contam no **primeiro** passo (o destino) e só quando o especialista não é estritamente maior; a BFS dos passos seguintes bloqueia apenas ocupação conservadora e obstáculos.
2. **PBT de consistência**: rotacionar o tabuleiro (helpers da U2) não muda a ação escolhida pelo especialista, exceto nos empates esquerda/direita decididos por sorteio.
3. **RNG dos agentes**: `SeedSequence([match_seed, 3_000_003, tick, snake_index])`; agentes são funções puras de `(state, snake_id)`, exceto o `HumanAgent` (buffer).
4. **HumanAgent**: filtrar ré e comandos redundantes no `push_absolute`, comparando com a direção **efetiva** (último comando do buffer ou, se vazio, a direção atual).
5. **Tempo de inferência** medido por um `TimedAgent` na camada `evaluation` (U7); `MatchService` continua sem relógio.
6. **Novo pacote `services/`** (fora do layout da D28): depende de `core` e `agents`; consumido por `ui`, `training` e `evaluation`.
**Demais respostas**: `act(state, snake_id)` no protocolo (Q1=B); `RandomAgent` uniforme sobre as ações não fatais, caindo para as três se todas forem fatais (Q2=B); espaço aceito por `flood > len(body)` (Q5=A); `MatchResult` mínimo + callback `on_tick` opcional (Q8=C); `sides` vem do chamador (Q9=A); aceite de 500 partidas e RNF03 como scripts + versões reduzidas no pytest (Q10=A); `tick`/`play` como funções de módulo (Q11=A); contrato como `typing.Protocol` (Q12=A).
**Origem**: Functional Design U3  
**Status**: Aprovada

## D45 — Complementos do Functional Design da U3
**Decisão**:
1. **Contratos de agente**:
   - `Agent.act(state, snake_id) -> Action` (todos os agentes).
   - `ExplainingAgent.decide(state, snake_id) -> ActResult` (opcional; só o `TreeAgent`). `ActResult` = ação executada + `ExplanationPayload`.
   - `MatchService.tick`: se o agente implementa `decide`, usa-o e repassa o `ActResult` pelo `on_tick`; senão usa `act`. **Nenhum agente guarda a última explicação em estado.**
2. **`HumanAgent.push_absolute` com buffer cheio**: **IGNORAR** a tecla nova (não descartar a mais antiga), porque cada comando foi validado em relação ao anterior — descartar o mais antigo quebraria a cadeia e poderia produzir marcha à ré. Teste obrigatório: direita, depois ↑ ← ↓ rápidos → buffer `[↑, ←]`, sem marcha à ré.
3. **Sincronizar `components.md` e `component-methods.md`**:
   - `agents.base`: `act(state, snake_id)`.
   - `agents.tree`: `decide(state, snake_id)`; `from_joblib` valida versão do **scikit-learn**, do **numpy** e o `FEATURE_SCHEMA_VERSION`.
   - `services.match`: `play(agent_a, agent_b, config, seed, sides, on_tick=None)`.
   - `core.features`: `feature_names() -> tuple[str, ...]`.
**Consequências**: substitui a regra BR-HUM-1 original (que descartava o mais antigo, como dizia a D28); `explain(state)` sai de `agents.tree` — a explicação chega à U7 pelo `ActResult` do `decide`, nunca recalculada nem guardada.
**Origem**: revisão do Functional Design U3  
**Status**: Aprovada

## D46 — NFR Requirements da U3
**Respostas**: Q1=B, Q2=A (com o BFS único), Q3=A, Q4=A, Q5=B, Q6=B, Q7=X.
**Medição que motivou as perguntas** (simulando a política da D44 sobre o código da U1, 30 partidas):
- Aleatório ingênuo (uniforme nas três ações): 12,9 ticks/partida, 22.921 partidas/min.
- Aleatório seguro (BR-RND-1): 433,4 ticks/partida, **812 partidas/min** — abaixo do piso de 1000 do RNF03.
- Custo por tick: `default_rng(SeedSequence([...]))` + um `integers` = **31,3 µs por agente** (37% do tick, mais que o `engine.step`); três `is_fatal` = 21,8 µs; `engine.step` = 25,5 µs.

**Decisão**:
1. **RNF03 por multiprocessing** (Q1=B, permitido pela D17): o piso de 1000 partidas/min é exigido da medição multiprocesso. Reportar também o número single-process **e ticks/s single-process**, que não depende da duração das partidas.
2. **Orçamento do especialista**: ≤ **1 ms** por decisão, **informativo com ALERTA** (como a D40), registrado no `benchmark.md`.
3. **Distância à comida com UM único BFS** a partir da comida, não três a partir dos destinos. Exato (não é aproximação): `next_occupancy` só difere entre as três ações na liberação da própria cauda, e a única ação que mantém a cauda sólida é a que pisa na comida — cuja distância é 0 por definição. Logo um BFS a partir da comida, com a cauda liberada, dá a distância correta de todos os destinos.
4. **Cobertura**: `source` passa a incluir `core`, `agents` e `services`, com o mesmo piso de **80%** por ramos (Q3=A).
5. **mypy estrito** estendido a `agents/` e `services/` (Q4=A).
6. **Contrato violado por agente**: `MatchService` valida que o retorno é um `Action` e levanta `TypeError` nomeando o agente e o lado (Q5=B).
7. **PBT**: `max_ticks` pequeno (ex.: 60) nos `CoreConfig` gerados, mantendo também o gerador `playing_state()` para propriedades de estado (Q6=B).
8. **Sorteio preguiçoso** (Q8=A): o `SeedSequence` só é construído quando um sorteio é realmente necessário. O especialista deixa de pagar os 31,3 µs (sorteia apenas em empate esquerda/direita); o `RandomAgent` continua pagando, e o piso do RNF03 vem do multiprocessing. Sem misturador próprio e sem `Generator` injetado.
9. **Localização** (Q7=X): o aceite de 95% é um teste pytest marcado `slow` (aprovado/reprovado natural e determinístico com seeds fixas); medições de throughput e latência ficam em `scripts/` (fora do pacote), porque produzem números para o `benchmark.md`.
**Origem**: NFR Requirements U3  
**Status**: Aprovada

## D47 — não utilizada
Número reservado e não usado: a decisão seguinte foi pedida explicitamente como D48. Registrado para que a lacuna não pareça um documento perdido.

## D48 — NFR Design da U3
**Respostas**: Q1=A, Q2=C, Q3=X, Q4=X, Q5=C.
**Decisão**:
1. **Multiprocessamento**: `Pool.imap_unordered` com `chunksize` explícito e `processes = cpu_count() - 1`. O worker recebe `(spec_a, spec_b, config, seed, sides)` — specs são descrições simples (nome + parâmetros) — e constrói os agentes localmente. Agregação independente da ordem; comparações ordenam por seed.
2. **`core/rng.py`**: registro único de todas as tags de stream (obstáculos, comida, helper da U1, agentes) e o helper genérico de `Generator` por tick. `setup`, `engine`, testes e agentes passam a importar dele. Novas streams (U5, U7) só podem ser criadas ali.
3. **Teste rápido**: ~20 seeds em modo sequencial e em paralelo produzem `MatchResult` idênticos. O teste `slow` de 500 partidas fica single-process.
4. **`benchmark.md` do especialista**: linha "kickoff sem obstáculos" (pior caso) e linha "média por decisão em partidas especialista vs. especialista".
5. **`evaluation/scoring.py`**: pontuação 1/0,5/0, taxa de vitória e taxa de empates; usado pelo aceite da U3 e estendido pela U7.
**Consequências**:
- `MatchResult` **deixa de carregar `score_a`** (que a D44/Q8 listava): a pontuação passa a ter um único dono em `evaluation/scoring.py`. `services` não importa `evaluation`, e `MatchResult` volta a ser só fatos da partida, com `outcome` como fonte da pontuação.
- O registro de streams é **preservador de valores**: as composições atuais (`[seed_k, 0]`, `[seed, tick_after]`, `[seed, 2_000_003]`) não mudam, só deixam de estar espalhadas. Trocar a composição mudaria os valores gerados e a reprodutibilidade histórica.
- Construção de agentes por spec exige um registro `nome → construtor` em `agents/`, porque o worker precisa construí-los do outro lado do `spawn` do Windows.
**Origem**: NFR Design U3  
**Status**: Aprovada

## D49 — Acréscimos ao plano de geração de código da U3
**Contexto**: plano aprovado com três acréscimos.
**Decisão**:
1. **Cobertura e mypy incluem `evaluation`**: o `source` da cobertura (≥ 80% por ramos) e os `files` do mypy estrito passam a ter `snake_vs_machine.evaluation`, além de `core`, `agents` e `services`. O pacote foi criado pela D48, depois que a D46 item 4/5 já havia fixado a lista — este item fecha a lacuna.
2. **P-EXP-MIRROR**: espelhar o tabuleiro inteiro (transformações da U2) troca `turn_left` ↔ `turn_right` na ação do especialista e mantém `straight`. Decisões com `drawn = True` são puladas. Complementa a P-EXP-ROT, que só usava rotações.
3. **Golden do especialista conferido manualmente**: distâncias à comida 14 (frente) / 16 (esquerda) / 14 (direita), empate de flood em 200, desempate final pela preferência por `straight`. Essas distâncias entram na tabela de avaliação esperada do teste, não apenas a ação escolhida.
**Consequências**:
- A nota de escopo da P-EXP-ROT ("apenas rotações, espelhos fora de escopo") é substituída: o espelho passa a ter uma propriedade própria, com a troca esquerda/direita como resultado esperado em vez de invariância.
- O piso de 80% por ramos agora vale também para `evaluation/batch.py`, cujo caminho multiprocesso é o mais difícil de cobrir; a cobertura vem do caminho sequencial e do teste de paridade da D48 item 3.
**Origem**: Code Generation U3 (Parte 1)  
**Status**: Aprovada

## D50 — Functional Design da U5
**Respostas**: Q1=A, Q2=B, Q3=A, Q4=X, Q5=C, Q6=C, Q7=X, Q8=A, Q9=C, Q10=A.
**Decisão**:
1. **Hiperparâmetros de produto**: `max_depth` ∈ {3, 6, 8}, `min_samples_leaf=1`, `criterion="gini"`, `class_weight="balanced"`. A grade experimental não altera os três arquivos. **Proibido** usar o conjunto de teste congelado para qualquer escolha de hiperparâmetro.
2. **DAgger**: 5 iterações sobre as três profundidades. Ao fim de **cada** iteração registrar acurácia no teste congelado e taxa vs. aleatório (1/0,5/0), para ver a curva.
3. **Dataset `.npz`**: por amostra `X`, `y`, `match_id`, `seed`, `tick`, `snake_index`, `pairing`, `dagger_iter`; metadados `FEATURE_SCHEMA_VERSION`, versão do numpy, `feature_names`.
4. **`DecisionTreeClassifier` com `random_state` fixo**, gravado no JSON. Treinar duas vezes no mesmo dataset produz árvores idênticas (teste obrigatório). A Code Generation entrega o pipeline e modelos-fixture pequenos. *(O momento do commit dos modelos reais foi revisto pela D52: ao fechar a U5, não “antes da U4”.)*
5. **Máscara, empate de proba** entre ações seguras: `straight` se estiver no empate; senão um sorteio no stream dos agentes (`[seed, 3_000_003, tick, snake_index]`).
6. **`TreeExplanation`**: `proposed`, `executed`, `vetoed`, `proba` (três valores na ordem de `_ACTIONS`), `path` de `PathStep(feature_name, threshold, feature_value, went_left)` da raiz até a folha.
7. **`predict_proba` mapeado via `classes_`**: classe ausente no treino tem probabilidade 0. Teste obrigatório com um modelo treinado sem uma das três ações.
8. **scikit-learn**: pin exato da versão que o `pip` resolver neste runtime, **compatível com `numpy==2.2.6`**, registrado em `decisions.md` e no JSON de cada modelo.
**Consequências**:
- `AgentSpec("tree", {"path": "...", "safety_mask": bool})` entra no registry da U3 (Q10=A).
- Falha de carga é `ModelLoadError` com `code="model_load"` e `reason` ∈ `{missing, sklearn, numpy, schema}` (Q8=A); U4 traduz para o erro 4 em PT.
**Origem**: Functional Design U5  
**Status**: Aprovada

## D51 — Pin do scikit-learn (U5)
**Decisão**: `scikit-learn==1.9.1` e `joblib==1.6.0` no `pyproject.toml` (dependências principais). Resolvido neste runtime Python 3.13.7 com `numpy==2.2.6` já instalado; `DecisionTreeClassifier` importa sem erro. O `pip` puxou `scipy==1.18.1` como dependência transitiva — não é pinada à parte. Essas duas versões entram no JSON de cada modelo.
**Origem**: Code Generation U5 Etapa 1 (D50 item 8)  
**Status**: Aprovada

## D52 — Escopo da Code Generation da U5
**Contexto**: plano aprovado com mudança de escopo — a U5 só fecha com os modelos reais.
**Decisão**:
1. **Fechamento exige o treino completo.** `train_bc.py` continua fora do pytest, mas rodar o treino e registrar os resultados é critério de fechamento: acurácia no teste congelado por profundidade (≥ 95% BC-6/8); curva da DAgger (acurácia e taxa vs. aleatório por iteração); 500 partidas vs. aleatório para BC-6 e BC-8 (≥ 90%, empates à parte); alerta D12 com 100 partidas; latência real com máscara ligada vs. 1 ms. Os três modelos reais são **commitados ao fim da U5**, não “antes da U4”.
2. **Sonda de 5% antes do treino cheio**: correr `train_bc.py` com ~5% das amostras, medir o tempo e extrapolar no `benchmark.md`. Coleta, DAgger e baterias usam o multiprocessamento de `evaluation.batch`.
3. **DAgger**: a cada iteração as **três** árvores (máscara off) jogam contra o especialista, **alternando lados**; o especialista rotula os estados das três; as linhas vão para **um** treino; as três são retreinadas. Cada iteração acrescenta ~**20 000** linhas (20% do dataset inicial).
4. **Coleta especialista vs. aleatório**: o especialista **alterna NW e SE** (D25). Grava-se o lado do especialista, qualquer que seja — não se assume lado A.
**Origem**: Code Generation U5 (Parte 1)  
**Status**: Aprovada

## D53 — Functional Design da U4
**Respostas**: Q1=A, Q2=A, Q3=X, Q4=A, Q5=A, Q6=B, Q7=B, Q8=A, Q9=A, Q10=B.
**Decisão**:
1. **Layout**: tabuleiro à esquerda (células quadradas); HUD + faixa RF05 empilhados à direita.
2. **Teclas**: setas e WASD no mesmo mapa absoluto.
3. **Durante a partida**: Esc → menu; P pausa/retoma; na pausa, N avança um tick e as teclas de movimento são ignoradas; R reinicia com nova seed.
4. **Espectador**: quaisquer dois de {Aleatório, Especialista, Fácil, Médio, Difícil}, inclusive iguais.
5. **Erro 4**: tela cheia em PT; qualquer tecla volta ao menu; motivo/caminho/traceback só no stderr.
6. **Fim**: overlay com resultado + `end_reason` + comprimentos; Enter = revanche (nova seed); Esc = menu. No espectador o texto usa o nome do agente, não "jogador/máquina".
7. **Painel até a U7**: stub `proposta` / `executada` / `vetado`; H continua ligando/desligando.
8. **Atraso**: no máximo um `tick` por frame; acumulador limitado a um período — sem dívida de ticks.
9. **pygame**: pin exato na Code Generation da U4 (nova D), como o sklearn.
10. **Janela**: `cell_px` no `config.yaml` (padrão 24); tamanho derivado; não redimensionável.
**Origem**: Functional Design U4  
**Status**: Aprovada

## D54 — Requisitos NFR da U4
**Respostas**: Q1=B, Q2=B, Q3=X, Q4=B, Q5=A, Q6=A, Q7=C, Q8=A.
**Decisão**:
1. **FPS**: script informativo em `scripts/`, com janela real (não dummy); média < 55 → **ALERTA** no `benchmark.md`; pytest nunca falha por FPS.
2. **pygame** e **pyyaml** no extra `[ui]`; o extra `dev` inclui `[ui]`.
3. **`ui/`** no mypy strict; verificar os stubs que acompanham o pygame 2.x; `ignore_missing_imports` só como fallback registrado.
4. **Cobertura**: `snake_vs_machine.ui` entra no gate de 80% por ramos, com omit apenas de `render.py`.
5. **Fonte TTF** com licença OFL commitada em `assets/fonts/`, com o arquivo de licença ao lado.
6. **`config.yaml`** via `--config` (default: `config.yaml` no diretório atual); ausente ou inválido → defaults + aviso no stderr.
7. **Sem vsync**; `Clock.tick(60)` é o único limitador.
8. **Testes** (Q5=A): a maioria importa só `keys` / `config` / helpers de relógio; um smoke com `SDL_VIDEODRIVER=dummy`. O script de FPS não usa dummy.
**Origem**: NFR Requirements U4  
**Status**: Aprovada

## D55 — Design NFR da U4
**Respostas**: Q1=B, Q2=C, Q3=C, Q4=A, Q5=B, Q6=A.
**Decisão**:
1. **Script de FPS**: 600 frames, espectador Difícil vs. Difícil, painel RF05 visível. Padrão: superfícies de texto (HUD e painel) em cache, renderizadas de novo só quando o conteúdo muda.
2. **Fonte e licença OFL** como package data em `snake_vs_machine/ui/fonts/`, lidas com `importlib.resources`; cópia em `assets/fonts/` para auditoria.
3. **`keys.py`** com apelidos por nome; só a camada Pygame conhece os códigos `K_*`.
4. **`ui_match_seed`** com tag **6_000_003** em `core/rng.py` (mesma forma do `collection_seed`). `session_seed` opcional: se ausente, `secrets.randbits(31)` no início da sessão, impresso no stderr.
5. **`models_dir`** no `config.yaml` (default `"models"`), resolvido em relação ao diretório do arquivo de config.
6. **Falha de display**: linha em português no stderr + mensagem técnica do SDL na linha seguinte; exit 1.
**Origem**: NFR Design U4  
**Status**: Aprovada

## D56 — Invariantes do registro de streams (`core/rng.py`)
**Contexto**: acréscimo ao plano de Code Generation da U4; a premissa de que comprimentos diferentes de `SeedSequence` separam streams é falsa.
**Decisão**:
1. **Caracterização**: `SeedSequence([5]).generate_state(4) == SeedSequence([5, 0]).generate_state(4)` é **True** neste numpy (zeros finais invisíveis). O docstring do módulo documenta esse fato e deixa de tratar o comprimento do vetor como isolador de streams.
2. **Invariante**: todas as tags distintas; todo contador que ocupa a posição de uma tag tem teto documentado (`tick` / `tick_after` ≤ `max_ticks`, `match_index` < 1_000_000) e fica abaixo da menor tag (`1_000_003`). Streams **novos**: tag sempre na **segunda** posição e diferente de todas as existentes.
3. **`ui_match_seed`**: tag `6_000_003`, forma igual a `collection_seed`; coberto pelos dois testes acima.
**Origem**: Code Generation U4 (escopo)  
**Status**: Aprovada

## D57 — Pins pygame e PyYAML
**Decisão**: `pygame==2.6.1` e `PyYAML==6.0.3` no extra `[ui]`; o extra `dev` repete os mesmos pins. Resolvido neste runtime Python 3.13.7; `import pygame` e `import yaml` ok. pygame 2.6.1 traz `py.typed` e stubs `.pyi` — mypy usa-os; **sem** `ignore_missing_imports` para `pygame.*`.
**Origem**: Code Generation U4 Etapa 1 (D53 Q9 / D54 item 2)  
**Status**: Aprovada

## D58 — `ui/session.py` puro (Code Generation U4)
**Decisão**:
1. Nova etapa antes do `render.py`: `ui/session.py`, lógica pura sem pygame (D53 item 6). Estado: tela (`menu` / `partida` / `pausa` / `fim` / `erro 4`), placar da sessão, `match_index`, modo e políticas. Entradas: eventos já traduzidos (alias de tecla, `dt`). Saídas: novo estado + comandos (`push_absolute`, `tick_with_results`, carregar políticas, sair). TDD obrigatório (testes vermelhos primeiro). Casos: pausa ignora movimento; **N** pausado = um tick; **R** e **Enter** = nova partida com `match_index + 1` via `ui_match_seed`; **Esc** = menu; placar acumula entre revanches e zera no menu; erro 4 em qualquer tela volta ao menu com qualquer tecla.
2. P-UI-PAUSE e P-UI-STEP testam `session.py` diretamente, sem pygame.
3. `screens.py` e `app.py` só traduzem pygame → alias, chamam `session`, executam comandos e desenham. `session.py` entra no gate de cobertura; só `render.py` permanece omitido.
**Origem**: Code Generation U4 (plano)  
**Status**: Aprovada

## D59 — Functional Design da U7
**Respostas**: Q1=A, Q2=B, Q3=X, Q4=X, Q5=X, Q6=X, Q7=A, Q8=X.
**Decisão**:
1. **`stress_results.md`**: seção **Diagnóstico** com causas de morte por modelo (`death_cause` dos `MatchResult`) e acurácia BC-3/6/8 só em estados críticos (alguma ação fatal **ou** especialista ≠ `straight`).
2. **Ruído**: wrapper da opção A; contínuos clipados em [0, 1]; `length_diff` sem ruído; stream tag **8_000_003**. Queda com máscara on e off (máscara lê o `State` real).
3. **Painel**: 3 últimas condições do `path`; texto `{rótulo} = {valor:.2f} ({≤|>} {limiar:.2f})` em `ui/explain_text.py` (puro, testado).
4. **`ui/labels_pt.py`**: dicionário sem pygame; teste `keys == feature_names()`. Relatórios da evaluation ficam em inglês.
5. **`scoring.py`**: IC normal com variância amostral dos escores 1/0,5/0; para D12, IC da **diferença** das duas baterias. Aprovação pela estimativa pontual.
6. **Seeds**: torneio tag **7_000_003**; ruído **8_000_003**. Scripts `torneio.py` + `estresse.py`; stub RF05 substituído no retângulo da U4.
7. **DoD**: Metrics em aprovado/reprovado honesto (Q1=A); estresse blocking = D12 500, 40% vs expert, ruído 10%; demais linhas do PRD reduzidas ou skipped (Q2=B). **TimedAgent** em `evaluation/timing.py` (Q7=A).
**Origem**: Functional Design U7  
**Status**: Aprovada

## D60 — Desenho experimental da Code Generation U7
**Decisão**:
1. **Pareado**: `tournament_seed(batch_seed, match_index)` — **sem** `pairing_code`. Forma: `SeedSequence([batch, 7_000_003, match_index])` então `integers`. Todas as baterias de uma mesma comparação compartilham a **mesma lista de seeds**. D12: BC-8 e BC-6. Ruído: limpo e ruidoso, máscara on e off. Lados alternam por índice (D25): índice par árvore = A/NW, ímpar = B/SE.
2. **`paired_difference_ci(xs, ys)`**: média das diferenças partida a partida ± 1,96 × (desvio amostral das diferenças) / √n. D12 e ruído reportam este intervalo. `n < 2` → `None`. Aprovação continua pela estimativa pontual (D59).
3. **Ruído**: N padrão **200** (pareado). Se o run usar N < 200, a célula no relatório é **indicativa**, não bloqueante.
4. **Pool no Windows (problema conhecido)**:
   - **Sintoma**: `multiprocessing.Pool.imap_unordered` pode travar (filhos spawnados, sem resultados, join não retorna).
   - **Onde**: `evaluation.batch.run_imap` com `processes > 1`. Observado na U5 (`train_bc` collect/DAgger/joblib). O throughput U3 random vs random com 15 workers **completou** neste host (4918,8 partidas/min).
   - **Contorno**: `--processes 1` (caminho in-process de `run_imap`).
5. **RNF03 reavaliado**: o piso ≥ 1000 partidas/min permanece **aprovado** pela medição U3 paralela (4918,8). Single-process continua abaixo (925,1 / baseline 812). U7 **não** re-mede RNF03; scripts U7 defaultam `--processes 1` por defesa após o hang da U5, não porque o RNF03 tenha sido revogado. Uma corrida U7 em `--processes 1` **não** substitui o número U3.
6. **Antes da Etapa 12**: mostrar as tabelas de diagnóstico N=50 (causas de morte + acurácia crítica) já medidas no FD.
**Origem**: Code Generation U7 (ajuste do plano)  
**Status**: Aprovada
