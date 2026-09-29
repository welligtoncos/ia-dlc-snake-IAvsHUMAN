# Unit of Work Plan — Snake vs. Máquina

Decomposição já fixada em requirements + D27–D29. Histórias puladas: o mapa usa RFs. Este plano registra as categorias obrigatórias e gera os artefatos na mesma passagem (Application Design aprovado + “seguir para Units Generation”).

## Execution checklist

- [x] Generate `unit-of-work.md`
- [x] Generate `unit-of-work-dependency.md`
- [x] Generate `unit-of-work-story-map.md`
- [x] Document code organization (monólito `src/snake_vs_machine`, D28; não `src/{unit}/`)
- [x] Validate boundaries (U6 fora; MatchService U3; queries U1)
- [x] Assign all in-scope RFs to units

## Questions (answered from approved decisions)

### Question 1 — Agrupamento
Como agrupar o trabalho?

A) Uma unit por U1–U7 do requirements (U6 omitida)

B) Uma única unit (monólito sem bolts)

X) Other (please describe after [Answer]: tag below)

[Answer]: A

### Question 2 — Dependências / ordem
A) Ordem D27: U1 → U2 → U3 → U5 → U4 → U7; cada unit só começa com aceite da anterior no caminho crítico

B) Paralelo U4 e U5 após U3

X) Other (please describe after [Answer]: tag below)

[Answer]: A — U5 antes de U4 de propósito (risco); U4 e U5 ambas dependem de U3, mas construction é sequencial

### Question 3 — Equipe
A) Um desenvolvedor (humano + agente AI-DLC), ownership por unit em sequência

B) Várias pessoas em paralelo por unit

X) Other (please describe after [Answer]: tag below)

[Answer]: A

### Question 4 — Implantação / código
A) Um processo desktop; pacote único `src/snake_vs_machine` (D28)

B) Um diretório `src/{unit-name}` por unit (padrão greenfield multi-unidade do code-generation.md)

X) Other (please describe after [Answer]: tag below)

[Answer]: A — D28 prevalece sobre a pasta por unit

### Question 5 — Domínio
A) Units alinhadas a núcleo / features / agentes / treino / UI / avaliação

B) Cortar por persona (jogador vs desenvolvedor)

X) Other (please describe after [Answer]: tag below)

[Answer]: A
