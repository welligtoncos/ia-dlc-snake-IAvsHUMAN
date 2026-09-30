"""Portuguese erro-4 copy (D53 / P-UI-ERR). Tracebacks stay off this string."""

from __future__ import annotations

TITLE = "Erro 4"
LEAD = "Não foi possível carregar o modelo da IA."

_REASON_LINES: dict[str, str] = {
    "missing": "O arquivo do modelo não foi encontrado.",
    "sklearn": "A versão do scikit-learn é incompatível com o modelo.",
    "numpy": "A versão do numpy é incompatível com o modelo.",
    "schema": "O esquema de features do modelo é incompatível.",
}


def window_text(reason: str) -> str:
    line = _REASON_LINES.get(reason)
    if line is None:
        raise ValueError(f"unknown model_load reason {reason!r}")
    return f"{TITLE}\n{LEAD}\n{line}"
