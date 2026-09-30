# Instruções de Testes de Integração

Não há rede, banco ou containers. Integração = unidades no mesmo processo.

## Propósito

Validar que `core` + `agents` + `services` + `evaluation` / `training` / `ui` combinam sem violar camadas.

## Cenários de Teste

### Cenário 1: MatchService + agentes (U1–U3)

- **Descrição**: `play` / `tick` / `tick_with_results` com `RandomAgent`, `ExpertAgent`, `HumanAgent`
- **Setup**: `pip install -e ".[dev]"`; sem serviços externos
- **Etapas de Teste**: `python -m pytest tests/services tests/agents/test_expert.py tests/evaluation/test_batch.py`
- **Resultados Esperados**: paridade sequencial/paralelo (`processes=1` no pytest); `MatchResult` sem score
- **Limpeza**: nenhuma

### Cenário 2: Árvore + features + máscara (U2 + U5)

- **Descrição**: `TreeAgent` carrega fixture/joblib, `extract_features`, `is_fatal`
- **Setup**: `models/fixtures/*.joblib` e, para testes de produto, `models/bc_depth3.joblib`
- **Etapas de Teste**: `python -m pytest tests/agents/test_tree.py tests/core/test_features.py`
- **Resultados Esperados**: `decide` == `act`; path `went_left` coerente com limiar
- **Limpeza**: nenhuma

### Cenário 3: Coleta / DAgger / scoring (U5 + U7)

- **Descrição**: `evaluation.batch` alimenta treino; `scoring` 1/0.5/0 e IC
- **Setup**: mesmo venv
- **Etapas de Teste**: `python -m pytest tests/training tests/evaluation`
- **Resultados Esperados**: seeds `collection_seed` / `dagger_seed` / `tournament_seed` estáveis
- **Limpeza**: não commitar `models/probe/` se gerar localmente

### Cenário 4: UI sessão + políticas (U4 + U7)

- **Descrição**: `session.py` sem pygame; `labels_pt` / `explain_text` sem `training`/`evaluation`
- **Setup**: extra `dev`
- **Etapas de Teste**: `python -m pytest tests/ui/test_session.py tests/ui/test_labels_pt.py tests/ui/test_explain_text.py`
- **Resultados Esperados**: teclas da D53; chaves PT == `feature_names()`
- **Limpeza**: nenhuma

## Configurar Ambiente de Testes de Integração

### 1. Iniciar Serviços Necessários

Nenhum. Não use docker-compose.

### 2. Configurar Endpoints dos Serviços

N/A — processo desktop.

## Executar Testes de Integração

### 1. Executar Suite

A suíte padrão já inclui os testes acima:

```bash
python -m pytest tests/services tests/evaluation tests/training tests/ui
```

`run_imap(..., processes=1)` permanece in-process (D60: evite `processes>1` em scripts longos neste Windows após o hang da U5).

### 2. Verificar Interações entre Serviços

- **Camadas**: `ui` não importa `training` nem `evaluation`; `services` não importa `evaluation`
- **Logs**: stdout do pytest

### 3. Limpeza

Nenhuma.
