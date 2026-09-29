# Unit–requirement map

Histórias de usuário puladas. Mapa: requisito / decisão → unit. Tudo in-scope está atribuído. RF08 e U6 não têm unit de implementação nesta versão.

| ID | Item | Unit |
| --- | --- | --- |
| Regras 1–10 | Tick, colisões, cauda, obstáculos | U1 |
| D25 | Spawns NW/SE, lados | U1 |
| D26 / D29 | Comida `(10,9)`; obstáculos; **todas** as livres 4-conectadas | U1 |
| `is_fatal` / `next_occupancy` / `flood_fill_*` | D29 + D32 + D33 (real vs conservador; testes (5,5)/(6,5) e cauda) | U1 |
| RF10 | config.yaml (subset núcleo) | U1 + U4 |
| RNF04, RNF11 | seed, 1800 ticks | U1 |
| Features 20 | `extract_features`, space_free, PBT D19 | U2 |
| RF01 | HumanAgent buffer 2 | U3 |
| RF06 (coleta/play headless) | MatchService.tick/play | U3 |
| Expert / random | U3 aceite 95% | U3 |
| RF02, RF03 | joblib, dificuldades, sklearn pin, erro 4 | U5 + U4 (UX) |
| D21, D27 alerta | teste congelado; D12 100 | U5 |
| D12 500, D22 | aceite + empates | U7 |
| RF04, RF07, RF09 | HUD, espectador, menu | U4 |
| RF05, D18 | painel + rótulos PT | U7 |
| RNF02 | 60 FPS, tick_rate visual | U4 |
| RNF03 | ≥ 1000/min random vs. random; throughput vs. especialista registrado | U3 (D30); U5/U7 reportam |
| D30 U1 | cobertura `core/` ≥ 80%; PBT `is_fatal`; PBT `setup` | U1 |
| D30 U5 | BC-8 ≥ 90% vs random; inferência < 1 ms com máscara = features+proba+mask (D40); ExplanationPayload | U5 |
| D30 U7 | BC-8 máscara ≥ 40% vs expert; ruído ≤ 15 pp; Metrics pass/fail | U7 |
| D30 DoD | ruff, pytest, hints, decisions.md, tag `uN-done` | Todas |
| RF08 | — | **Won't** (D03) |
| U6 VIPER | — | **Won't** (D08) |

## Persona overlay (sem stories.md)

| Persona | Units |
| --- | --- |
| Jogador casual | U4, U7 (painel), U3 (humano) |
| Desenvolvedor | U3 headless, U5, U7 torneio/estresse |
