# Instruções de Testes de Desempenho

Informativos. **pytest nunca falha** por tempo, FPS ou partidas/min (D34/D40/D46/D54).

## Requisitos de Desempenho

| ID | Meta | Onde | Gate |
| --- | --- | --- | --- |
| RNF03 | >= 1000 partidas/min random vs random | multiprocess | U3: 4918.8 (aprovado). Single-process ~925, abaixo do piso. D60: não re-medir com `--processes 1` |
| Expert | <= 1 ms / decisão (ALERTA) | `scripts/expert_latency.py` | U3 kickoff 0.427 ms OK |
| Features | <= 0.5 ms pior caso (ALERTA) | U2 `benchmark.md` | ALERTA 2.12 ms |
| Árvore | <= 1 ms (ALERTA) | `scripts/bc_latency.py` | U5 **1.48 ms ALERTA** |
| FPS | média >= 55 (ALERTA se < 55) | `scripts/ui_fps.py` | U4 média 60.78 OK |
| D12 / ruído | ver `reports/stress_results.md` | `torneio.py`, `estresse.py` | D12 aprovado; ruído reprovado |

Não há meta de “usuários concorrentes” nem taxa de erro HTTP.

## Configurar Ambiente de Testes de Desempenho

### 1. Preparar Ambiente de Teste

```bash
python -m pip install -e ".[dev]"
```

Display real para `ui_fps.py`. Headless para throughput/latência.

### 2. Configurar Parâmetros de Teste

Definidos em cada script (n partidas, 600 frames, n=200 kicks). Não há JMeter/k6.

## Executar Testes de Desempenho

### 1. Throughput (RNF03)

```bash
python scripts/throughput.py
```

Neste Windows, se `Pool` travar, não force workers: o número U3 paralelo permanece a evidência do RNF03 (D60).

### 2. Latência

```bash
python scripts/expert_latency.py
python scripts/bc_latency.py
```

### 3. FPS

```bash
python scripts/ui_fps.py
```

Janela real, 600 frames, espectador Difícil vs Difícil, painel visível. Média < 55 → ALERTA em `aidlc-docs/construction/u4-ui/benchmark.md`.

### 4. Estresse / torneio (já medido na U7)

```bash
python scripts/torneio.py --n 500 --batch-seed 0 --processes 1
python scripts/estresse.py --n 200 --batch-seed 0 --processes 1
```

Longo (BC-8 tende a timeout). Resultados: `reports/stress_results.md`.

### 5. Analisar Resultados

- Compare com as tabelas nos `benchmark.md` de U1–U5 e `reports/stress_results.md`
- Gargalo conhecido: `extract_features` / flood fill; latência da árvore com máscara

## Otimização de Desempenho

Fora do escopo de Build e Testes. Retrain e VIPER estão fora desta versão.
