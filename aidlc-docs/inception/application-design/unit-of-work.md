# Units of Work — Snake vs. Máquina

**Tipo**: monólito (um serviço implantável: app desktop + CLIs). Units = módulos lógicos / bolts, não microsserviços.

**Código (D28, override do default `src/{unit}/`)**:

```
src/snake_vs_machine/{core,agents,training,evaluation,ui}
tests/   # espelha o pacote
pyproject.toml   # pip install -e .
```

**Ordem de construction (D27)**: U1 → U2 → U3 → U5 → U4 → U7. U6 fora desta versão.

## U1 — Core
**Responsibilities**: `state`, `setup` (D25/D26/D29), `engine` (só tick; passo 5 via `next_occupancy`), `queries` (`is_fatal` D32, `next_occupancy`, `flood_fill_count`, `reachable_cells`).  
**Aceite**: regras 1–10; D26/D29 conectividade total; teste oponente-comida; 1000 partidas aleatórias; 1800 ticks; **cobertura core/ ≥ 80%**; **PBT is_fatal**; **PBT setup** (D30).  
**DoD**: D30 (ruff, pytest, hints, decisions.md, tag `u1-done`).  
**NFR stages**: sim.

## U2 — Features
**Responsibilities**: `extract_features`; usa `flood_fill_count` / `reachable_cells`.  
**Aceite**: features manuais + PBT rotação/espelhamento; `space_free_*`.  
**DoD**: D30 (tag `u2-done`). CG must remove `omit = ["*/features.py"]` from `pyproject.toml` (see `construction/plans/u2-features-code-generation-plan.md`).  
**NFR stages**: sim.

## U3 — Agents + MatchService
**Responsibilities**: `Agent.act`; random, expert, human (buffer 2); **MatchService** (`tick` sem relógio).  
**Aceite**: expert ≥ 95% vs random (1/0,5/0) em 500; **RNF03 ≥ 1000 partidas/min random vs. random**; throughput vs. especialista **registrado**.  
**DoD**: D30 (tag `u3-done`).  
**NFR stages**: sim.

## U5 — Behavior Cloning
**Responsibilities**: `agents.tree` devolve **ação + ExplanationPayload**; collect, DAgger, modelos 3/6/8; alerta D12 100.  
**Aceite**: acurácia ≥ 95% BC-6/8; BC-6 **e BC-8** ≥ 90% vs random; inferência < 1 ms **com máscara** = `extract_features` + `predict_proba` + `safety_mask` (D40); alerta D12 100.  
**DoD**: D30 (tag `u5-done`).  
**NFR stages**: não (D27).

## U4 — UI
**Responsibilities**: Pygame, menu, HUD, espectador; ritmo `tick_rate`; consome MatchService.  
**Aceite**: RF01, RF04, RF07, RF09; 60 FPS; erro 4 em PT.  
**DoD**: D30 (tag `u4-done`).  
**NFR stages**: sim.

## U7 — Explain + stress
**Responsibilities**: dicionário PT + render do payload da U5; torneio 500; estresse; `reports/stress_results.md`.  
**Aceite**: D12 +10 pp em 500; BC-8 máscara **≥ 40%** vs especialista; ruído 10% **≤ 15 pp**; tabela Metrics toda aprovado/reprovado.  
**DoD**: D30 (tag `u7-done`).  
**NFR stages**: não (D27).

**DoD comum (D30)**: `ruff` limpo; `pytest` verde; type hints nas APIs públicas; `decisions.md` atualizado; commit + tag `uN-done`.
