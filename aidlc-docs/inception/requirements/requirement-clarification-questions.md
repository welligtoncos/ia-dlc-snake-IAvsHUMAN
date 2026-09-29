# Esclarecimento — Análise de Requisitos

Detectei uma contradição entre o PRD e as respostas:

**Contradição: RF03 (Must) vs. U6 fora do escopo**

- O PRD define RF03 como Must: três dificuldades — Fácil (profundidade 3), Médio (profundidade 6) e Difícil (árvore VIPER).
- Q4: MVP até U5 + U7 completa; U6 VIPER no próximo ciclo.
- Q8: C — não treinar PPO nesta versão.

Sem U6 não existe a árvore VIPER da dificuldade Difícil.

---

## Clarification Question 1
Como tratar a dificuldade Difícil (RF03) nesta versão, sem VIPER?

A) Só Fácil (BC-3) e Médio (BC-6) no menu; Difícil entra com o VIPER no próximo ciclo

B) Três opções no menu; Difícil visível mas desabilitada, com aviso de que vem no próximo ciclo

C) Difícil nesta versão usa uma árvore BC de profundidade 8 como placeholder até o VIPER

X) Other (please describe after [Answer]: tag below)

[Answer]:X — Difícil nesta versão usa uma árvore BC de profundidade 8 com a mascara_seguranca ligada. Quando o VIPER chegar no próximo ciclo, ele substitui essa configuração se tiver taxa de vitória maior contra o especialista. RF03 continua Must, com a definição do Difícil atualizada no PRD.
