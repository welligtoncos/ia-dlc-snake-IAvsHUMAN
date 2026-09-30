# Como a IA do Snake vs. Máquina foi treinada

Este texto explica, em linguagem de aula, o que a “máquina” aprendeu e o que ela **não** é. Os números vêm da corrida real de treino (`scripts/train_bc.py`) e dos relatórios em `aidlc-docs/construction/u5-bc/benchmark.md` e `reports/stress_results.md`.

## A ideia em uma frase

A IA **não** joga milhares de partidas “para ganhar pontos” como um reforço clássico. Ela **imita um especialista escrito à mão**: em cada situação, o especialista escolhe uma ação (`reto`, `virar esquerda`, `virar direita`) e a árvore de decisão tenta repetir essa escolha.

Isso se chama **clonagem de comportamento** (*behavior cloning*, BC).

## Quem é o “professor”

O professor é o `ExpertAgent` (`src/snake_vs_machine/agents/expert.py`). Não é uma rede neural. É uma heurística, nesta ordem:

1. **Não morrer** — evita ações fatais (parede, obstáculo, corpo).
2. **Não ficar sem espaço** — prefere o lado com mais células livres (flood fill).
3. **Ir à comida** — distância por um BFS a partir da comida (não três buscas a partir da cabeça).

Quando duas ações empatam, um sorteio determinístico (seed da partida + tick) desempata.

A árvore **não** copia o código do especialista. Ela só vê um **vetor de números** extraído do tabuleiro e um **rótulo** (qual das três ações o especialista teria jogado).

## O que a árvore “enxerga”

Antes de cada tick, `extract_features` monta **20 números** no ponto de vista da cobra (frente / esquerda / direita):

| Tipo | Exemplos |
| --- | --- |
| Perigo | `danger_*`, `dist_danger_*` |
| Espaço | `space_free_*` |
| Comida | `food_*`, `dist_food`, `opponent_closer_to_food` |
| Adversário | `dist_opponent_head`, `head_risk_*` |
| Corpo | `length_diff` (diferença de comprimento) |

A mesma lista está em `feature_names()`. O painel do jogo (tecla **H**) mostra as **últimas 3 condições** do caminho da árvore, em português — isso é só **explicação** do modelo já treinado, não um segundo treino.

## As três dificuldades

O sklearn ajusta três `DecisionTreeClassifier` no **mesmo** conjunto de dados, com profundidade máxima **3, 6 e 8** (Fácil / Médio / Difícil):

| Hiperparâmetro | Valor |
| --- | --- |
| `criterion` | gini |
| `min_samples_leaf` | 1 |
| `class_weight` | balanced |
| `random_state` | 0 |

Arquivos gerados: `models/bc_depth{3,6,8}.joblib` + um `.json` ao lado (versões de sklearn/numpy e nomes das features). Se o pin de sklearn ou o esquema de features mudar, o jogo recusa o modelo (**Erro 4**).

## Passo 1 — Coletar exemplos (BC inicial)

O script joga partidas e, a cada tick, grava o vetor de features e a ação do **especialista** (não a ação da árvore — ainda não existe uma boa árvore).

Dois tipos de partida:

- **Especialista vs especialista** — jogos longos, muitos ticks “fáceis”.
- **Especialista vs aleatório** — o adversário erra; o especialista vê estados mais estranhos.

Meta da coleta: pelo menos **100 000** linhas (na prática foram **123 848**, porque as partidas longas passam do mínimo).

As seeds dessas partidas vêm de `collection_seed` em `core/rng.py` (reproduzível).

## Passo 2 — Separar treino e teste *por partida*

Não se embaralha tick a tick. O corte é **80/20 por `match_id`**: o teste congelado tem **23 202** linhas de só **13** partidas. Assim a árvore não “decora” o mesmo jogo no treino e no teste.

Hiperparâmetros **não** foram escolhidos olhando esse teste: ele só mede o quanto a árvore ainda imita o especialista em partidas que ela nunca viu.

## Passo 3 — DAgger (corrigir o desvio)

Um problema clássico da clonagem: a árvore erra um pouco, o tabuleiro vai para um estado que o especialista quase nunca viu, e o erro **acumula**.

**DAgger** (Dataset Aggregation) faz isto, **5 vezes**:

1. As três árvores jogam contra o especialista.
2. Em cada tick da **cobra-aluna**, grava-se o estado **dela**, mas o rótulo é “o que o especialista faria **agora**”.
3. Essas linhas entram no conjunto de treino (~**20 000** por iteração; no fim **205 812** linhas).
4. As três árvores são **retreinadas do zero** no conjunto aumentado.

Não se “afina” a árvore velha: cada iteração gera de novo os três `.joblib`.

```text
Coleta (especialista joga)
        |
        v
   Fit inicial  -->  teste congelado
        |
        +-- DAgger 1..5: aluno joga, professor rotula, concatena, refit --+
                                                                          |
                                                                          v
                                                              models/bc_depth3,6,8
```

## Passo 4 — Máscara de segurança (não é treino)

Na partida, a árvore pode propor uma ação **fatal**. Com a máscara ligada (Difícil no produto), o jogo troca por uma ação segura usando as **probabilidades da mesma árvore** e o tabuleiro **real** — sem reler o vetor. Isso **não** entra no `fit`. Fácil e Médio saem de fábrica **sem** máscara.

## Quanto “colou” no especialista (teste congelado)

Acurácia = fração de ticks em que `predict` = rótulo do especialista no teste que **nunca** entrou no `fit`.

| Momento | Prof. 3 | Prof. 6 | Prof. 8 |
| --- | ---: | ---: | ---: |
| Fit inicial | 67,7% | 92,4% | 96,2% |
| Depois do DAgger 5 | 61,1% | 94,7% | **96,5%** |

A barra interna era ≥ 95% para as profundidades 6 e 8: **só a 8 passou**. A 6 ficou em 94,7% (na iteração 4 tinha 96,1% e depois caiu).

**Imitar bem o especialista no teste ≠ ganhar o jogo.** Contra o aleatório em 500 partidas (máscara desligada): BC-6 **36,8%** e BC-8 **75,2%** dos pontos (meta informal era 90%). Contra o próprio especialista, a BC-8 com máscara tende a **empate por tempo** (as duas sobrevivem até o limite de ticks).

O ruído de 10% nas features derruba a pontuação bem mais que 15 pontos percentuais — a árvore é frágil quando o vetor mente.

## Como repetir o treino

Demora (a corrida cheia levou **~46 minutos** neste projeto). No Windows, use um processo só se o `Pool` travar:

```bash
python scripts/train_bc.py --fraction 1.0 --out-dir models --processes 1
```

Sonda rápida (~5% dos dados):

```bash
python scripts/train_bc.py --fraction 0.05 --out-dir models/probe --vs-random-n 8 --acceptance-n 0 --d12-n 0 --processes 1
```

O treino **não** roda no `pytest` padrão.

## Como *ver* o que a árvore decidiu (sem retreinar)

```bash
python scripts/jogo.py
```

Escolha 1/2/3 e deixe o painel visível (**H**). Cada linha do caminho é uma pergunta do tipo: “esta feature é ≤ ou > que este limiar?”. Isso é o `decision_path` do sklearn, traduzido em `ui/explain_text.py`.

## Leitura extra (técnica)

| Arquivo | Conteúdo |
| --- | --- |
| `src/snake_vs_machine/training/collect.py` | Coleta BC |
| `src/snake_vs_machine/training/dagger.py` | DAgger |
| `src/snake_vs_machine/training/fit.py` | Fit das três profundidades |
| `scripts/train_bc.py` | Orquestra coleta + fit + DAgger + baterias |
| `aidlc-docs/construction/u5-bc/benchmark.md` | Tabelas da corrida cheia |
| `reports/stress_results.md` | D12 e ruído depois do treino |
