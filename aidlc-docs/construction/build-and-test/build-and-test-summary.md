# Resumo de Build e Testes

Medição nesta máquina após aprovar a U7 (2026-09-30): `ruff` + `mypy` + `pytest --cov --cov-branch`.

## Status do Build

- **Ferramenta de Build**: pip + setuptools (`pip install -e ".[dev]"`)
- **Status do Build**: Sucesso
- **Artefatos de Build**: pacote `snake_vs_machine` em `src/`; modelos em `models/`
- **Tempo de Build**: ruff + mypy < 15 s; suíte ~8 min 51 s
- **ruff**: All checks passed
- **mypy**: Success, 43 source files

## Resumo da Execução de Testes

### Testes Unitários

- **Total de Testes**: 277 passed + 2 deselected (`slow`)
- **Passaram**: 277
- **Falharam**: 0
- **Cobertura**: 85.29% ramos (piso 80%; omit `ui/render.py`)
- **Status**: Passou

### Testes de Integração

- **Cenários de Teste**: MatchService, TreeAgent+features, batch/treino/scoring, UI sessão/RF05 (na mesma suíte)
- **Passaram**: inclusos nos 277
- **Falharam**: 0
- **Status**: Passou
- **Serviços externos**: nenhum

### Testes de Desempenho

| Medição | Real | Meta | Status |
| --- | --- | --- | --- |
| RNF03 random vs random (U3 parallel) | 4918.8 /min | >= 1000 | Passou (herdado; D60) |
| Expert kickoff | 0.427 ms | <= 1 ms | OK |
| BC-8 kickoff | 1.48 ms | <= 1 ms | ALERTA (U5) |
| FPS médio (U4) | 60.78 | >= 55 | OK |
| D12 gap (U7) | 0.422 | >= 0.10 | aprovado |
| BC-8 vs expert | 0.500 | >= 0.40 | aprovado |
| Ruído 10% drop | 0.440 / 0.480 | <= 0.15 | reprovado |

- **Status**: scripts informativos executados na Construction; ruído fora da meta (honesto)

### Testes Adicionais

- **Testes de Contrato**: N/A (sem API)
- **Testes de Segurança**: N/A (Security Baseline desabilitada)
- **Testes E2E**: smoke `tests/ui/test_smoke.py` na suíte; `jogo.py` / `ui_fps.py` manuais

## Status Geral

- **Build**: Sucesso
- **Todos os Testes** (gate padrão): Passou
- **Pronto para Operations**: Sim, no sentido de encerrar Construction. Operations é **placeholder** (D27) — sem deploy/monitoramento nesta versão

## Arquivos de instrução

- `build-instructions.md`
- `unit-test-instructions.md`
- `integration-test-instructions.md`
- `performance-test-instructions.md`
- `e2e-test-instructions.md`
- `build-and-test-summary.md`

Sem `contract-test-instructions.md` nem `security-test-instructions.md`.

## Próximos Passos

Construction completa do ponto de vista de código e gate de testes. Operations não tem workflow de implantação neste projeto.
