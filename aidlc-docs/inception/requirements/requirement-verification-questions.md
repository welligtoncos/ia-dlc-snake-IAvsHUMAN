# Perguntas de Esclarecimento — Análise de Requisitos

Responda cada pergunta preenchendo a letra após a tag `[Answer]:`.
Se nenhuma opção servir, escolha a última (Outro) e descreva a preferência na mesma linha.

Fonte da intenção: `PRD/PRD — Snake vs. Máquina (IA com Árvore de Decisão) · AI-DLC.md`

---

## Question 1
Qual é o modo principal de disputa entre humano e máquina?

A) Mesmo tabuleiro 20x20, duas cobras, mesma comida (como o PRD descreve)

B) Cada um em seu próprio tabuleiro, competindo só por pontuação

C) Mesmo tabuleiro no modo padrão, com opção extra de tabuleiros separados

X) Other (please describe after [Answer]: tag below)

[Answer]:A

## Question 2
Como o painel "Por que a IA fez isso?" (RF05) deve aparecer durante a partida?

A) Sempre visível ao lado do tabuleiro

B) Só quando o jogador pausa

C) Sempre visível, com tecla para ocultar/mostrar

X) Other (please describe after [Answer]: tag below)

[Answer]:C

## Question 3
A gravação das partidas do humano para treinar uma árvore no estilo do jogador (RF08) entra neste MVP?

A) Não — RF08 fica fora do MVP (Could)

B) Sim — gravar partidas no MVP, mas treinar essa árvore só depois

C) Sim — gravar e treinar a árvore do jogador já neste MVP

X) Other (please describe after [Answer]: tag below)

[Answer]:A

## Question 4
Qual é o recorte desta versão em relação às 7 units do PRD?

A) Entregar as 7 units nesta execução (U1 núcleo até U7 explicação e estresse), incluindo VIPER

B) MVP até U5 (Behavior Cloning + dificuldades Fácil/Médio); U6 VIPER e U7 ficam para depois

C) MVP até U5 + painel de explicação e torneio (parte de U7), sem VIPER

X) Other (please describe after [Answer]: tag below)

[Answer]:X — MVP até U5 + U7 completa (painel de explicação, torneio e testes de estresse com as árvores BC-3 e BC-6). U6 VIPER fica para o próximo ciclo.

## Question 5
O modo espectador IA vs. IA com interface gráfica (RF07, Could) entra nesta versão?

A) Não — só IA vs. IA sem GUI (RF06)

B) Sim — incluir modo espectador com Pygame

X) Other (please describe after [Answer]: tag below)

[Answer]:B

## Question 6
Em qual idioma ficam o menu, o HUD e o painel de explicação?

A) Português

B) Inglês

C) Português na interface, identificadores de código em inglês

X) Other (please describe after [Answer]: tag below)

[Answer]:C

## Question 7
Qual velocidade padrão do jogo para o humano (tick fixo)?

A) 10 ticks por segundo (mais lento, didático)

B) 15 ticks por segundo (ritmo clássico de Snake)

C) Configurável só via `config.yaml`, sem valor rígido no PRD além de 60 FPS de renderização

X) Other (please describe after [Answer]: tag below)

[Answer]:X — 10 ticks por segundo como padrão, configurável via config.yaml; renderização a 60 FPS.

## Question 8
Qual é o limite de computação para treinar o professor PPO do VIPER (se U6 estiver no escopo)?

A) CPU apenas, treino curto (minutos a poucas horas); se não convergir, usar o especialista como professor do VIPER

B) GPU disponível; treino PPO completo conforme o PRD

C) U6 fora desta versão — não treinar PPO agora

X) Other (please describe after [Answer]: tag below)

[Answer]:C

## Question 9
As regras da extensão de segurança devem ser aplicadas neste projeto?

A) Sim — aplicar todas as regras SECURITY como restrições bloqueantes (recomendado para aplicações de nível de produção)

B) Não — pular todas as regras SECURITY (adequado para PoCs, protótipos e projetos experimentais)

X) Other (please describe after [Answer]: tag below)

[Answer]:B

## Question 10
O baseline de resiliência deve ser aplicado neste projeto?

Ativá-lo aplica melhores práticas direcionais de design (AWS Well-Architected — Reliability Pillar): tolerância a falhas, disponibilidade, observabilidade e recuperabilidade. Não certifica produção nem garante RTO/RPO.

A) Sim — aplicar o baseline de resiliência como melhores práticas direcionais e orientação de design

B) Não — pular o baseline de resiliência (adequado para PoCs, protótipos e projetos experimentais)

X) Other (please describe after [Answer]: tag below)

[Answer]:B

## Question 11
As regras de testes baseados em propriedades (PBT) devem ser aplicadas neste projeto?

A) Sim — aplicar todas as regras PBT como restrições bloqueantes (recomendado para lógica de negócio, transformações de dados ou componentes com estado)

B) Parcial — aplicar PBT apenas para funções puras e round-trips de serialização (ex.: `extrair_features`, serialização de estado)

C) Não — pular todas as regras PBT

X) Other (please describe after [Answer]: tag below)

[Answer]:B
