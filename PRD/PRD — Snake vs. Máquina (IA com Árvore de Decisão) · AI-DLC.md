# PRD — Snake vs. Máquina (IA com Árvore de Decisão) · AI-DLC

Sep 28, 2026 · @ton

## Visão geral

Snake vs. Máquina é um jogo Snake em Python no qual o jogador humano disputa o mesmo tabuleiro com uma cobra controlada por uma IA baseada em árvore de decisão. A IA é treinada por Behavior Cloning (imitando um agente especialista) e, numa segunda fase, por VIPER (destilação de uma política de Reinforcement Learning para uma árvore).

O diferencial do produto é a **IA explicável**: durante a partida, o jogador pode ver a regra da árvore que motivou cada movimento da máquina (por exemplo, `perigo_frente = 1 e comida_esquerda = 1 → virar à esquerda`).

O projeto também serve como bancada de experimentos: a mesma IA é submetida a testes de estresse (ruído, atraso, mapas novos) para medir onde ela falha.

**Público:** o próprio desenvolvedor (portfólio e estudo de IA) e jogadores casuais que queiram enfrentar e entender uma IA.

**Metodologia:** o desenvolvimento segue o AI-DLC (AI-Driven Development Lifecycle), em que um agente de IA propõe planos, design e código, e o humano valida cada etapa.

## Objetivos e métricas

O MVP está pronto quando a IA de árvore vence um jogador aleatório em pelo menos 90% das partidas e roda a 60 FPS sem travar.

| Objetivo | Métrica | Meta |
| --- | --- | --- |
| IA competitiva | Taxa de vitória vs. agente aleatório | ≥ 90% em 500 partidas |
| IA competitiva | Taxa de vitória vs. especialista (A\* + heurística) | ≥ 40% |
| Fidelidade da imitação | Acurácia da árvore vs. ações do especialista (conjunto de teste) | ≥ 95% |
| IA explicável | Profundidade máxima da árvore | ≤ 8 níveis |
| Desempenho | Tempo de inferência por jogada | < 1 ms |
| Desempenho | Taxa de quadros | 60 FPS estáveis |
| Robustez | Queda de desempenho com 10% de ruído nas features | ≤ 15 pontos percentuais |
| Qualidade de código | Cobertura de testes do núcleo (`core/`) | ≥ 80% |

**Não objetivos (fora do escopo desta versão):**

- Multiplayer online ou em rede
- IA baseada em redes neurais como produto final (redes só entram como professoras no VIPER)
- Versão mobile ou web
- Gráficos elaborados, sons ou skins

## Como usar este PRD no AI-DLC

Este PRD é a **Intent** (intenção de alto nível) que alimenta o agente de IA na fase de Inception. O agente propõe, pergunta e gera; o humano aprova antes de cada avanço. O AI-DLC foi apresentado pela AWS em 2025 e organiza o trabalho em três fases, com ciclos curtos chamados *bolts* no lugar de sprints e *Units of Work* no lugar de épicos ([Wiz](https://www.wiz.io/academy/ai-security/ai-driven-development-lifecycle-ai-dlc), [Codewave](https://codewave.com/feeds/blog/aws-ai-sdlc)).

| Fase | O que a IA faz | O que o humano valida | Artefato gerado em `aidlc-docs/` |
| --- | --- | --- | --- |
| Inception | Lê este PRD, faz perguntas de esclarecimento, gera user stories e divide em Units of Work | Regras do jogo, features da IA, metas das métricas | `requirements.md`, `user-stories.md`, `units.md` |
| Construction | Propõe o design de cada unit, gera código e testes a cada bolt | Design dos módulos, código, resultado dos testes | `design/<unit>.md`, código em `src/`, testes em `tests/` |
| Operations | Empacota o jogo, gera relatórios de avaliação e documentação | Resultados do torneio e dos testes de estresse | `README.md`, `reports/stress_results.md` |

**Regras de trabalho com o agente:**

1. Cada bolt entrega uma unit testável, em horas ou poucos dias.
2. O agente sempre apresenta um plano antes de escrever código e espera aprovação.
3. Toda decisão aprovada fica registrada em `aidlc-docs/decisions.md` para manter o contexto entre bolts.
4. Nenhuma unit avança com testes falhando.

## Regras do jogo e requisitos funcionais

Humano e máquina controlam cada um uma cobra no mesmo tabuleiro de 20 × 20 células e disputam a mesma comida; vence quem sobreviver ou tiver a maior cobra ao fim do tempo.

**Regras:**

1. As duas cobras começam com 3 segmentos, em cantos opostos, andando para o centro.
2. Existe sempre 1 comida no tabuleiro; comer aumenta a cobra em 1 segmento e gera nova comida em célula livre.
3. Uma cobra morre ao bater na parede, no próprio corpo ou no corpo da adversária.
4. Colisão cabeça com cabeça: morre a menor; se forem do mesmo tamanho, empate.
5. A partida termina quando uma cobra morre ou após 3 minutos; no tempo esgotado, vence a maior.
6. O jogo roda em ticks fixos: as duas cobras se movem ao mesmo tempo a cada tick.

**Requisitos funcionais:**

| ID | Requisito | Prioridade |
| --- | --- | --- |
| RF01 | Controle do humano pelas setas ou WASD | Must |
| RF02 | Cobra da máquina controlada por um modelo carregado de arquivo (`.joblib`) | Must |
| RF03 | Três dificuldades: Fácil (`bc_depth3`, máscara off), Médio (`bc_depth6`, máscara off) e Difícil (`bc_depth8` com `mascara_seguranca` ligada). VIPER só no próximo ciclo, e só substitui o Difícil se vencer mais o especialista. | Must |
| RF04 | HUD com placar, tamanho das cobras e tempo restante | Must |
| RF05 | Painel "Por que a IA fez isso?" exibindo a regra da árvore usada no último movimento | Should |
| RF06 | Modo IA vs. IA, sem interface gráfica, para rodar torneios e coletar dados | Must |
| RF07 | Modo espectador: assistir IA vs. IA com interface gráfica | Could |
| RF08 | Gravação das partidas do humano (estado → ação) para treinar a IA com o estilo do jogador | Could |
| RF09 | Menu inicial com escolha de dificuldade e modo | Should |
| RF10 | Configuração de tamanho do tabuleiro e velocidade por arquivo `config.yaml` | Should |

## Especificação da IA

A IA é um `DecisionTreeClassifier` (scikit-learn) que recebe um vetor de features relativas à direção da cabeça e devolve uma de 3 ações: **seguir em frente, virar à esquerda ou virar à direita**. Ações relativas (em vez de cima/baixo/esquerda/direita) deixam a árvore menor e sem movimentos suicidas de marcha a ré.

### Features

| Feature | Tipo | Descrição |
| --- | --- | --- |
| `perigo_frente`, `perigo_esq`, `perigo_dir` | 0/1 | Parede, próprio corpo ou corpo do oponente na célula adjacente |
| `dist_perigo_frente`, `dist_perigo_esq`, `dist_perigo_dir` | 0–1 | Distância até o primeiro obstáculo em cada direção, normalizada pelo tamanho do tabuleiro |
| `espaco_livre_frente`, `espaco_livre_esq`, `espaco_livre_dir` | 0–1 | Células alcançáveis (flood fill) após o movimento, dividido pelo total de células livres; evita que a cobra se encurrale |
| `comida_frente`, `comida_esq`, `comida_dir`, `comida_tras` | 0/1 | Em qual semiplano relativo está a comida |
| `dist_comida` | 0–1 | Distância de Manhattan até a comida, normalizada |
| `oponente_mais_perto_comida` | 0/1 | O oponente chega à comida antes de mim |
| `dist_cabeca_oponente` | 0–1 | Distância até a cabeça do oponente, normalizada |
| `risco_cabeca_frente`, `risco_cabeca_esq`, `risco_cabeca_dir` | 0/1 | A célula de destino pode ser ocupada pela cabeça do oponente no mesmo tick |
| `diff_tamanho` | inteiro | Meu tamanho menos o do oponente (define se colisão de cabeça me favorece) |

Todas as features são calculadas por uma única função `extrair_features(estado, id_cobra)`, usada no treino e no jogo, para não haver divergência entre os dois.

### Agente especialista (professor do Behavior Cloning)

O especialista é determinístico e não usa aprendizado:

1. Calcula o caminho até a comida com A\*, tratando os corpos e as possíveis próximas posições da cabeça do oponente como obstáculos.
2. Só aceita o primeiro passo do caminho se o espaço livre após o movimento (flood fill) for maior que o tamanho da cobra.
3. Se não houver caminho seguro, escolhe o movimento com mais espaço livre (modo sobrevivência).

### Fase 1: Behavior Cloning

1. Rodar partidas especialista vs. especialista e especialista vs. aleatório no modo sem interface, gravando pares `(features, ação)`. Meta: 100 mil amostras.
2. Dividir em 80% treino e 20% teste por partida (não por amostra), para evitar vazamento.
3. Treinar com busca em grade sobre `max_depth` (3 a 12), `min_samples_leaf` (1 a 50) e `criterion` (gini, entropy), usando `class_weight="balanced"` porque "seguir em frente" domina os dados.
4. Aplicar DAgger por 3 a 5 iterações: a árvore joga, o especialista rotula os estados que ela visitou, e os dados são agregados e a árvore retreinada. Isso corrige erros em estados que o especialista nunca visitaria.
5. Salvar os modelos `bc_depth3.joblib`, `bc_depth6.joblib` e `bc_depth8.joblib` (Fácil, Médio e Difícil desta versão).

### Fase 2: VIPER (próximo ciclo — não entra nesta versão)

Nesta versão a dificuldade Difícil é BC profundidade 8 com `mascara_seguranca` ligada. O VIPER fica para o próximo ciclo.

1. Criar um ambiente Gymnasium `SnakeVersusEnv` com o mesmo vetor de features e o oponente sendo o especialista.
2. Treinar um professor PPO com Stable-Baselines3. Recompensas: +10 comida, −10 morte, +20 vitória, −0,01 por tick.
3. Rodar o VIPER: coletar estados com a política atual, rotular com a ação do PPO e dar peso a cada amostra pela diferença entre o maior e o menor valor Q (estados em que errar custa caro pesam mais), retreinar a árvore e repetir por N iterações.
4. Escolher a árvore com maior taxa de vitória em validação, limitada a profundidade 8, e salvar como `viper.joblib`.

### Inferência e explicação

A cada tick o jogo chama `modelo.predict()` e usa `decision_path()` para recuperar os nós percorridos, que o painel RF05 exibe como regra legível:

```python
def explicar(arvore, x, nomes):
    t = arvore.tree_
    regras = []
    for no in arvore.decision_path([x]).indices:
        if t.children_left[no] == -1:  # folha
            break
        f, lim = t.feature[no], t.threshold[no]
        sinal = "<=" if x[f] <= lim else ">"
        regras.append(f"{nomes[f]} {sinal} {lim:.2f}")
    return " E ".join(regras)
```

Uma flag `mascara_seguranca` (desligada por padrão) impede a IA de escolher uma ação com morte imediata; ela existe para comparar a árvore pura com a árvore protegida nos testes de estresse. Na dificuldade Difícil desta versão a máscara fica ligada.

## Requisitos não funcionais e arquitetura

O núcleo do jogo é puro Python e independente da interface gráfica, para que a mesma lógica rode no Pygame, no ambiente Gymnasium e nos torneios sem interface.

**Requisitos não funcionais:**

| ID | Requisito |
| --- | --- |
| RNF01 | Python 3.11+, rodando em Windows, Linux e macOS |
| RNF02 | Inferência da IA abaixo de 1 ms por jogada; 60 FPS na interface |
| RNF03 | Modo sem interface capaz de simular pelo menos 1.000 partidas por minuto para coleta de dados |
| RNF04 | Reprodutibilidade: toda partida e todo treino aceitam `seed` e registram a seed usada |
| RNF05 | Código tipado (type hints), formatado com `ruff` e testado com `pytest` |
| RNF06 | Modelos versionados em `models/` com um `.json` ao lado registrando dados, hiperparâmetros e métricas |

**Stack:** `pygame` (interface), `numpy` (estado e features), `scikit-learn` e `joblib` (árvore), `gymnasium` e `stable-baselines3` (professor PPO do VIPER), `pytest`, `matplotlib` (gráficos dos relatórios), `pyyaml` (configuração).

**Estrutura de pastas:**

```
snake-vs-maquina/
├── aidlc-docs/            # artefatos do AI-DLC (requisitos, units, decisões)
├── config.yaml
├── src/
│   ├── core/              # regras do jogo, sem dependência de pygame
│   │   ├── estado.py      # tabuleiro, cobras, comida
│   │   ├── motor.py       # tick, colisões, fim de partida
│   │   └── features.py    # extrair_features()
│   ├── agentes/
│   │   ├── base.py        # interface Agente.agir(estado) -> acao
│   │   ├── aleatorio.py
│   │   ├── especialista.py  # A* + flood fill
│   │   ├── arvore.py      # carrega .joblib, predict + explicar
│   │   └── humano.py      # teclado
│   ├── treino/
│   │   ├── coletar.py     # gera dataset com o especialista
│   │   ├── behavior_cloning.py
│   │   ├── dagger.py
│   │   ├── env_gym.py     # SnakeVersusEnv
│   │   └── viper.py
│   ├── avaliacao/
│   │   ├── torneio.py
│   │   └── estresse.py    # wrappers de ruído, atraso, sticky actions
│   └── ui/
│       ├── jogo.py        # loop pygame, HUD
│       └── painel_explicacao.py
├── models/
├── data/
├── reports/
└── tests/
```

Todo agente implementa a mesma interface `agir(estado) -> acao`, então humano, especialista, aleatório e árvore são intercambiáveis em qualquer modo de jogo.

## Units of Work e bolts

O projeto tem 7 units, executadas em ordem; cada uma só começa quando os critérios de aceite da anterior passam.

| Unit | Entrega | Depende de | Critérios de aceite |
| --- | --- | --- | --- |
| U1 — Núcleo do jogo | `core/estado.py`, `core/motor.py` | — | Testes cobrem as 6 regras, incluindo colisão cabeça com cabeça e empate; 1.000 partidas aleatórias sem exceção |
| U2 — Features | `core/features.py` | U1 | Testes com tabuleiros montados à mão conferem cada feature; mesma saída para a mesma entrada |
| U3 — Agentes base | aleatório, especialista, humano | U1, U2 | Especialista vence o aleatório em ≥ 95% de 500 partidas |
| U4 — Interface | `ui/jogo.py`, HUD, menu | U1, U3 | Humano joga contra o especialista a 60 FPS; RF01, RF04 e RF09 atendidos |
| U5 — Behavior Cloning | coleta, treino, DAgger, `bc_depth3`, `bc_depth6` e `bc_depth8` | U2, U3 | Acurácia ≥ 95% no teste; taxa de vitória ≥ 90% vs. aleatório (BC-6/BC-8); profundidade ≤ 8 |
| U6 — VIPER | `env_gym.py`, PPO, `viper.py`, `viper.joblib` | U2, U5 | **Fora desta versão.** No próximo ciclo: árvore VIPER substitui o Difícil se a taxa de vitória vs. especialista for maior que a da BC-8 com máscara |
| U7 — Explicação e estresse | painel RF05, `torneio.py`, `estresse.py`, relatório | U4, U5 | Painel mostra a regra a cada movimento; `reports/stress_results.md` gerado com BC-3, BC-6 e BC-8 (sem VIPER) |

**Checklist de cada bolt:**

- [ ] Agente apresenta o plano da unit e as perguntas em aberto
- [ ] Humano aprova o plano e registra decisões em `decisions.md`
- [ ] Agente gera código e testes
- [ ] Testes passam e critérios de aceite são verificados
- [ ] Humano revisa o código e libera a próxima unit

## Plano de testes de estresse

Cada teste roda 500 partidas por nível contra o especialista, com seeds fixas, e compara as três árvores desta versão (BC-3, BC-6, BC-8) com o próprio especialista como referência. VIPER entra na comparação só no próximo ciclo.

| Teste | Variável | Níveis | O que revela |
| --- | --- | --- | --- |
| Profundidade | `max_depth` da árvore BC | 1 a 15 | Ponto de overfitting e a menor árvore competitiva |
| Ruído nas features | Ruído gaussiano nas features contínuas e bits invertidos nas binárias | 0%, 5%, 10%, 20%, 30% | Sensibilidade aos limiares dos nós |
| Sticky actions | Probabilidade de repetir a ação anterior | 0%, 10%, 25% | Capacidade de se recuperar de erros |
| Atraso de ação | Ticks entre decidir e executar | 0, 1, 2 | Antecipação |
| Mudança de mapa | Tamanho do tabuleiro (treino em 20 × 20) | 10 × 10, 30 × 30, 40 × 40 | Generalização fora da distribuição |
| Obstáculos | Paredes internas geradas aleatoriamente | 0, 5, 15 blocos | Generalização para situações nunca vistas |
| Feature removida | Zerar uma feature por vez | Cada uma das 20 features | Importância real de cada feature (compara com `feature_importances_`) |
| Poucos dados | Tamanho do dataset de BC | 1 mil, 10 mil, 100 mil | Eficiência de dados da árvore |
| Máscara de segurança | `mascara_seguranca` | Ligada, desligada | Quantas derrotas são erros bobos de morte imediata |

**Métricas registradas por partida:** vencedor, duração em ticks, comidas coletadas, causa da morte (parede, próprio corpo, oponente, cabeça com cabeça) e tempo médio de inferência.

**Saída:** para cada teste, um gráfico de taxa de vitória por nível com intervalo de confiança de 95% e uma tabela de causas de morte, em `reports/stress_results.md`.

## Riscos, questões em aberto e prompts

**Riscos:**

| Risco | Impacto | Mitigação |
| --- | --- | --- |
| Árvore imita mal o especialista em estados raros | IA morre em situações simples | DAgger e `class_weight="balanced"` |
| PPO não converge e o VIPER fica sem professor | Dificuldade Difícil atrasa | Começar com tabuleiro 10 × 10; se falhar, usar o especialista como professor do VIPER |
| Árvore profunda demais para explicar | Painel RF05 ilegível | Limite de profundidade 8 e mostrar só as 3 condições mais próximas da folha |
| Divergência entre features de treino e de jogo | IA joga pior que nos testes | Uma única função `extrair_features` e teste de igualdade entre os dois caminhos |
| Flood fill lento em tabuleiros grandes | Queda de FPS | Limitar a busca a 200 células e usar `numpy` |

**Questões em aberto:**

- [x] Modo principal: mesmo tabuleiro 20x20, duas cobras, mesma comida.
- [x] Painel de explicação sempre visível, com tecla para ocultar/mostrar.
- [x] RF08 (gravar/treinar no estilo do jogador) fora deste MVP.

**Prompts sugeridos para o agente de IA:**

1. *Inception:* "Leia o PRD em `aidlc-docs/prd.md`. Liste as ambiguidades e faça as perguntas necessárias antes de gerar `requirements.md`, `user-stories.md` e `units.md`. Não escreva código."
2. *Construction (por unit):* "Vamos iniciar o bolt da unit U2 — Features. Proponha o design de `features.py` e os casos de teste, com um tabuleiro de exemplo para cada feature. Aguarde minha aprovação antes de implementar."
3. *Revisão:* "Rode os testes, compare o resultado com os critérios de aceite da U5 no PRD e liste o que passou, o que falhou e por quê."
4. *Operations:* "Rode `avaliacao/estresse.py` com todos os testes do PRD e gere `reports/stress_results.md` com gráficos e um resumo de onde cada árvore falha."
