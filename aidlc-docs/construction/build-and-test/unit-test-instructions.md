# Execução de Testes Unitários

A suíte padrão **exclui** testes marcados `slow` (`addopts = -m not slow`). Não roda torneio N=500.

## Executar Testes Unitários

### 1. Executar Todos os Testes Unitários

```bash
python -m pytest
```

Com cobertura por ramos (piso 80%, omit `ui/render.py`):

```bash
python -m pytest --cov --cov-branch
```

PBT no perfil curto (padrão):

```bash
python -m pytest
```

PBT no perfil cheio (mais exemplos; mais lento):

```bash
set HYPOTHESIS_PROFILE=full
python -m pytest
```

(No POSIX: `HYPOTHESIS_PROFILE=full python -m pytest`.)

Só um pacote:

```bash
python -m pytest tests/core tests/agents tests/services tests/evaluation tests/training tests/ui
```

### 2. Revisar Resultados dos Testes

- **Esperado**: todos os testes não-`slow` passam (última medição Construction: **276 passed**, 2 deselected `slow`)
- **Cobertura de Testes**: >= **80%** por ramos no `source` do `pyproject.toml` (última medição: **85.33%**)
- **Localização do Relatório**: stdout do pytest-cov; sem diretório HTML gerado por padrão

### 3. Corrigir Testes com Falha

1. Leia o traceback no terminal
2. Isolar: `python -m pytest path/to/test_file.py::test_name -vv`
3. Corrija o código ou o teste
4. Reexecute até verde; depois `python -m ruff check` e `python -m mypy`

O aceite expert >= 95% vs random em 500 partidas é `slow` (D46) e **não** entra no gate padrão.
