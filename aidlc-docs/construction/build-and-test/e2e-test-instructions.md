# Instruções de Testes End-to-End

Fluxo jogável é um processo Pygame local (RF01). Sem browser e sem API.

## Smoke automático (sem janela)

```bash
set SDL_VIDEODRIVER=dummy
python -m pytest tests/ui/test_smoke.py
```

Abre uma surface, desenha o menu uma vez. Faz parte da suíte padrão.

## Partida manual

```bash
python scripts/jogo.py --config config.yaml
```

- Humano NW, árvore SE (política do menu 1/2/3)
- Esc / P / N / R / H conforme D53
- Painel RF05: veto + até 3 condições em PT (`explain_text`)
- Erro 4: modelo ausente ou pin quebrado → tela PT; traceback só no stderr

## Espectador

No menu, Tab escolhe dois agentes (D53). Sem teclas de movimento.

## FPS (E2E de render)

`python scripts/ui_fps.py` — ver `performance-test-instructions.md`.

## Contrato / segurança

N/A. Sem API. Security Baseline desabilitada. Sem arquivo de contract/security tests.
