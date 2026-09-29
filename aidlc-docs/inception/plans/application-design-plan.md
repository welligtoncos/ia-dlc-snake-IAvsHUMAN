# Application Design Plan — Snake vs. Máquina

## Purpose

Definir componentes, métodos de alto nível, serviços e dependências. Regras detalhadas de U1 (incluindo D26) já estão em `requirements.md`; este estágio só fecha limites e contratos.

## Execution checklist (Part 2)

- [x] Generate `aidlc-docs/inception/application-design/components.md`
- [x] Generate `aidlc-docs/inception/application-design/component-methods.md`
- [x] Generate `aidlc-docs/inception/application-design/services.md`
- [x] Generate `aidlc-docs/inception/application-design/component-dependency.md`
- [x] Generate `aidlc-docs/inception/application-design/application-design.md` (consolidado)
- [x] Validate: core sem pygame; `Agent.act`; U1 contém spawn `(10,9)`, obstáculos D26, 1800 ticks
- [x] Validate: U6/VIPER ausente dos componentes desta versão

## Already decided (do not re-ask)

- Monólito Python em `src/` (core, agents, training, evaluation, ui)
- Código em inglês; UI em português
- `safety_mask` e `extract_features` conforme D19–D24 e D26
- Sem Gymnasium/PPO nesta versão
- D27: ordem U1-U2-U3-U5-U4-U7; NFR só U1–U4; alerta D12 na U5
- D28: setup vs engine; MatchService U3; queries; buffer humano; pacote instalável; sklearn pin

## Questions

### Question 1
Como cortar os componentes do núcleo (U1/U2)?

A) Três módulos: `state` (tabuleiro/cobras), `engine` (tick/colisões/D26), `features` (vetor) — obstáculos gerados no engine/state

B) Quatro módulos: os três acima mais `obstacles.py` só para zona livre, simetria e flood fill de conectividade

X) Other (please describe after [Answer]: tag below)

[Answer]: X — core = state, engine (só tick), features + setup.py (spawns, comida, obstáculos D26)

### Question 2
Quem orquestra um tick da partida?

A) Serviço `MatchService`: lê ações dos dois agentes e chama `engine.step` — Pygame e headless usam o mesmo serviço

B) O loop Pygame chama `engine.step` direto; o headless duplica um loop mínimo sem serviço compartilhado

X) Other (please describe after [Answer]: tag below)

[Answer]: A — MatchService na U3; step/tick sem relógio; UI e headless no ritmo; HumanAgent buffer 2, 1 por tick

### Question 3
Onde vive `safety_mask` (D24)?

A) Em `agents.tree` (só a política de árvore aplica a máscara)

B) No `engine` como filtro pós-ação, opcional por cobra (qualquer agente pode usar máscara)

X) Other (please describe after [Answer]: tag below)

[Answer]: X — máscara em agents.tree; core.queries: is_fatal e flood_fill; PBT is_fatal False ⇒ sem morte determinística no tick simulado

### Question 4
Layout de pacote greenfield?

A) `src/` com subpacotes `core`, `agents`, `training`, `evaluation`, `ui` (como o PRD)

B) Pacote instalável `snake_vs_machine/` na raiz, mesmos subpacotes

X) Other (please describe after [Answer]: tag below)

[Answer]: X — src/snake_vs_machine/{core,agents,training,evaluation,ui} + pyproject.toml + pip install -e .

Note: Q1–Q4 = decisões humanas D28 (não defaults). Item 5: sklearn pinado, erro 4.
