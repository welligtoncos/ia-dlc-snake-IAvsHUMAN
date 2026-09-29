# Story Generation Plan — Snake vs. Máquina

## Purpose

Converter `requirements.md` (aprovado, D01–D25) em personas e histórias INVEST, organizadas para virar Units of Work (U1–U5, U7).

## Recommended approach (default if you pick A on Q2)

**Híbrido Unit + jornada**: cada Unit é um epic; dentro dela, histórias seguem a jornada (jogar / treinar / avaliar) só quando a unit tem UI. U1–U3 são histórias de regra/agente; U4/U7 misturam jogador e desenvolvedor.

### Decomposition options (trade-offs)

| Approach | Benefit | Cost |
| --- | --- | --- |
| A) Por Unit (recomendado) | Encaixa nos bolts U1–U7; menos retrabalho na Geração de Unidades | Histórias de núcleo menos “como usuário” |
| B) Só jornada do jogador | Melhor narrativa de UX | Treino/estresse ficam órfãos |
| C) Só por RF | Rastreio 1:1 | Estoura INVEST (histórias grandes ou fragmentadas) |
| D) Por persona | Clareza de público | Duplica o mesmo núcleo duas vezes |

## Execution checklist (Part 2 — do not run until this plan is approved)

- [ ] Generate `aidlc-docs/inception/user-stories/personas.md` (personas from Q1)
- [ ] Generate `aidlc-docs/inception/user-stories/stories.md` using the chosen decomposition
- [ ] Ensure each story is Independent, Negotiable, Valuable, Estimable, Small, Testable
- [ ] Add acceptance criteria per story in the format from Q4
- [ ] Map each story to persona(s), RF/NFR/Dn, and target unit (U1–U5, U7)
- [ ] Exclude U6/VIPER and RF08 from this version’s stories (could/next cycle only as “won’t”)
- [ ] Cover D13–D14, D22–D25 in acceptance of the matching stories
- [ ] Verify no story depends on PPO/Gymnasium

## Story constraints (already decided — do not re-ask)

- UI em português; código em inglês
- Escopo: U1–U5 + U7; sem VIPER; sem RF08
- Partida 1800 ticks; teclas absolutas; taxa 1 / 0,5 / 0
- Spawns NW/SE; torneios alternam lados
- Modelos entregues 3, 6, 8; teste BC congelado pré-DAgger

## Questions

Preencha a letra após cada `[Answer]:`. Use X e descreva se nenhuma opção servir.

### Question 1
Quais personas devem aparecer em `personas.md`?

A) Duas: Jogador casual e Desenvolvedor (treino, torneio, estresse) — alinhado ao PRD

B) Três: Jogador casual, Desenvolvedor, e Espectador (só assiste IA vs. IA)

C) Uma: Desenvolvedor-jogador (a mesma pessoa joga e avalia)

X) Other (please describe after [Answer]: tag below)

[Answer]:

### Question 2
Como decompor as histórias?

A) Por Unit (U1 núcleo, U2 features, U3 agentes, U4 UI, U5 BC, U7 explicação/estresse) — recomendado para ir às Units em seguida

B) Por jornada: menu → partida → painel → espectador; treino/estresse como epics à parte

C) Híbrido: Units como epics e, dentro de U4/U7, histórias por jornada do jogador

X) Other (please describe after [Answer]: tag below)

[Answer]:

### Question 3
Qual granularidade?

A) 1–3 histórias por unit (mais grossas, um bolt ≈ poucas histórias)

B) Várias histórias pequenas por unit (uma regra/feature de aceite por história)

C) Uma história por requisito funcional (RF01–RF10) mais histórias técnicas de U1/U2/U5

X) Other (please describe after [Answer]: tag below)

[Answer]:

### Question 4
Formato dos critérios de aceitação?

A) Given / When / Then (português)

B) Lista de bullets testáveis (português), sem Gherkin

X) Other (please describe after [Answer]: tag below)

[Answer]:

### Question 5
Como priorizar as histórias dentro de cada unit?

A) Ordem das units (U1→U7) e, dentro da unit, Must → Should; Could (RF08) fora

B) Só Must nesta versão; Should (RF05, RF07, RF09, RF10) como histórias “se der tempo” no fim da unit

X) Other (please describe after [Answer]: tag below)

[Answer]:

---

Quando terminar, avise (por exemplo “pronto”). A geração de `stories.md` e `personas.md` só começa depois da aprovação deste plano.
