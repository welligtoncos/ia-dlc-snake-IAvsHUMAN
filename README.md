# Snake vs. Máquina

Jogo de Snake em que **você** joga contra uma **árvore de decisão** (sklearn), não contra uma rede neural. O objetivo didático é tornar visível o que uma árvore realmente faz: uma sequência de perguntas do tipo “este número é ≤ ou > que este limiar?” até chegar a uma folha (`reto` / `virar esquerda` / `virar direita`).

```bash
python -m pip install -e ".[dev]"
python scripts/jogo.py
```

Python **≥ 3.13**. No menu: **Enter** joga, **1/2/3** escolhe Fácil/Médio/Difícil, **Tab** é espectador. **H** liga ou desliga o painel de explicação.

## Por que uma árvore (e não um “cérebro” opaco)

Uma árvore de classificação é um fluxograma aprendido a partir de exemplos:

1. Em cada **nó interno** há **uma feature** e um **limiar**.
2. Se o valor atual é **≤ limiar**, desce pela esquerda; se é **>**, pela direita.
3. A **folha** guarda a classe (aqui, uma das três ações relativas).
4. A **profundidade** máxima limita quantas perguntas cabem no caminho. Fácil = 3, Médio = 6, Difícil = 8.

Não há camadas escondidas. Se você anotar as perguntas do painel, está lendo o mesmo `decision_path` que o sklearn usou para aquele tick.

### Exemplo (como ler o painel)

O jogo mostra as **3 condições mais perto da folha**, neste formato:

```text
comida à frente = 1.00 (> 0.50)
dist. perigo à frente = 0.10 (≤ 0.25)
espaço livre à esquerda = 0.80 (> 0.40)
```

Leia cada linha assim: “olhei a feature X; o valor agora é V; por isso tomei o ramo ≤ ou > do limiar T”. Juntas, elas são o **final do caminho** da raiz até a folha. Acima delas o painel ainda diz:

- **proposta** — o que a árvore pediu
- **executada** — o que de fato foi jogado
- **vetado** — se a **máscara de segurança** trocou uma ação fatal (só no Difícil, por padrão)

A máscara **não** é a árvore: ela usa o tabuleiro real (`is_fatal`) depois do `predict`. Serve para você ver a diferença entre “o modelo quis” e “o jogo deixou”.

## O que a árvore enxerga (e o que não enxerga)

Antes de decidir, o jogo vira o tabuleiro num vetor de **20 números** no ponto de vista da cobra (frente / esquerda / direita): perigo, espaço livre, comida, cabeça do oponente, diferença de comprimento.

A árvore **nunca** vê pixels, nem o código do especialista. Só esse vetor. Por isso duas partidas que “parecem iguais” na tela podem cair em folhas diferentes se um bit do vetor mudou.

Lista oficial: `feature_names()` em `src/snake_vs_machine/core/features.py`. Rótulos em português: `src/snake_vs_machine/ui/labels_pt.py`.

## De onde vêm as três árvores

Elas **não** foram desenhadas à mão. Foram **ajustadas** (clonagem de comportamento) para imitar um especialista heurístico:

- o especialista joga; cada tick vira um exemplo `(vetor, ação)`
- o sklearn cresce a árvore (gini, `max_depth` 3/6/8)
- o **DAgger** acrescenta estados em que o *aluno* jogou, rotulados de novo pelo especialista — para corrigir o desvio quando a árvore erra e o jogo sai do “mundo” do professor

Arquivos prontos: `models/bc_depth3.joblib`, `bc_depth6.joblib`, `bc_depth8.joblib` (e o `.json` ao lado, com versões e nomes das features).

Passo a passo do treino, com números reais: [docs/como-a-ia-foi-treinada.md](docs/como-a-ia-foi-treinada.md).

Para **aprender a árvore**, o caminho curto é jogar e olhar o painel — não reler o sklearn.

## Como usar o jogo para estudar

1. Comece no **Fácil (1)**. Caminhos curtos: poucas perguntas, regras mais “grosseiras”.
2. Repita a mesma abertura no **Difícil (3)**. Mais profundidade = mais cortes no espaço das 20 features; o caminho no painel muda.
3. Pause (**P**) e avance um tick (**N**). Compare proposta vs executada quando a cobra está encurralada.
4. No **espectador (Tab)**, coloque duas árvores iguais ou árvore vs especialista e só observe o painel.

Perguntas úteis enquanto joga:

- Esta folha é “sempre reto” ou só neste canto do tabuleiro?
- O limiar faz sentido (ex.: `danger_ahead = 1`)?
- A máscara salvou uma morte que a árvore não viu?

## Controles

| Tecla | Efeito |
| --- | --- |
| Setas ou WASD | Movimento (absoluto no mapa) |
| P | Pausa / continua |
| N | Um tick (só na pausa) |
| R | Nova partida (outra seed) |
| H | Painel da árvore |
| Esc | Menu (ou sair no menu) |
| Enter | Jogar / revanche no overlay de fim |

`--config` aponta para um YAML (padrão: `config.yaml` no diretório atual). Sem `session_seed`, uma seed aleatória é impressa no stderr.

## Testes e avaliação

```bash
python -m pytest
python scripts/torneio.py --n 50 --processes 1
```

A suíte padrão não retreina e não roda o torneio de 500 partidas. Dependências e pins: `pyproject.toml` (não use o `requirements.txt` antigo da pasta `PRD/`).

## Mapa do código (o essencial)

| Pasta | Papel |
| --- | --- |
| `src/snake_vs_machine/core/` | Tabuleiro, `step`, features |
| `src/snake_vs_machine/agents/` | Especialista, árvore, humano, ruído |
| `src/snake_vs_machine/services/` | Loop da partida |
| `src/snake_vs_machine/training/` | Coleta, DAgger, fit |
| `src/snake_vs_machine/ui/` | Pygame + texto do caminho |
| `scripts/jogo.py` | Entrada do jogador |
| `models/` | Árvores já treinadas |

O fluxo AI-DLC (requisitos, decisões D01–D60) está em `aidlc-docs/`. Não é necessário para entender a árvore no jogo.
