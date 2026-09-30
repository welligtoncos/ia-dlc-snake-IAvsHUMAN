# Instruções de Build

Desktop Python (monólito). Não há compilação nativa nem artefato de servidor.

## Pré-requisitos

- **Ferramenta de Build**: pip + setuptools (`pyproject.toml`), backend `setuptools.build_meta`
- **Python**: >= 3.13 (D37). Medido neste host: 3.13.7
- **Dependências de runtime**: `numpy==2.2.6`, `scikit-learn==1.9.1`, `joblib==1.6.0` (D51)
- **Extra UI**: `pygame==2.6.1`, `PyYAML==6.0.3` (D57)
- **Extra dev**: pytest, pytest-cov, hypothesis, ruff, mypy + pins UI
- **Variáveis de Ambiente**: nenhuma obrigatória. Opcionais:
  - `HYPOTHESIS_PROFILE=dev` (padrão) ou `full` (D34)
  - `SDL_VIDEODRIVER=dummy` para smoke Pygame sem janela
- **Requisitos de Sistema**: Windows 10/11 ou POSIX; ~500 MB para venv + modelos. Display só para `scripts/jogo.py` e `scripts/ui_fps.py`
- **Modelos de produto**: `models/bc_depth{3,6,8}.joblib` + `.json` (U5)

## Etapas de Build

### 1. Instalar Dependências

Na raiz do workspace:

```bash
python -m pip install -e ".[dev]"
```

Isso instala o pacote `snake-vs-machine` em modo editável, o extra `dev` (inclui pins UI) e as deps de teste.

Só runtime + UI, sem ferramentas de teste:

```bash
python -m pip install -e ".[ui]"
```

### 2. Configurar Ambiente

Nenhuma variável obrigatória. Confirme o interpretador:

```bash
python --version
python -c "import snake_vs_machine, numpy, sklearn, pygame; print('ok')"
```

### 3. Compilar Todas as Unidades

Não há `compile` separado. O install editável cobre U1–U7 (`core`, `agents`, `services`, `evaluation`, `training`, `ui`).

Verificação estática (gate de Construction):

```bash
python -m ruff check src tests scripts
python -m mypy
```

### 4. Verificar Sucesso do Build

- **Saída Esperada**: ruff `All checks passed`; mypy `Success: no issues found`
- **Artefatos de Build**:
  - pacote importável em `src/snake_vs_machine/`
  - modelos em `models/`
  - fonte OFL em `src/snake_vs_machine/ui/fonts/`
- **Avisos Comuns**:
  - pip pode imprimir conflitos de extras de outros pacotes do sistema; o pin de `numpy==2.2.6` deve permanecer
  - mypy ignora stubs ausentes de `sklearn.*`, `joblib`, `yaml` (registrado no `pyproject.toml`)

## Solução de Problemas

### Build Falha com Erros de Dependência

- **Causa**: Python < 3.13; ou numpy/sklearn/pygame fora do pin
- **Solução**: use 3.13+; reinstale com `python -m pip install -e ".[dev]"`; não atualize numpy/sklearn/pygame sem nova D

### Build Falha com Erros de Compilação

- **Causa**: ruff E501/I001 ou mypy strict em módulo novo
- **Solução**: `python -m ruff check --fix src tests scripts`; corrija tipos; `python -m mypy`
