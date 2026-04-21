"""Tool de busca web usando DuckDuckGo (sem API key)."""

from __future__ import annotations

from shared.logger import get_logger

log = get_logger(__name__)

TOOL_DEFINITION = {
    "name": "web_search",
    "description": "Busca informações na web usando DuckDuckGo. Use para perguntas sobre fatos atuais.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Termos de busca"},
            "max_results": {"type": "integer", "description": "Número de resultados (padrão: 5)", "default": 5},
        },
        "required": ["query"],
    },
}


def web_search(query: str, max_results: int = 5) -> str:
    """Executa busca no DuckDuckGo e retorna snippets dos resultados."""
    try:
        from ddgs import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        if not results:
            return "Nenhum resultado encontrado."
        lines = []
        for i, r in enumerate(results, 1):
            lines.append(f"[{i}] {r.get('title', 'Sem título')}")
            lines.append(f"    {r.get('body', 'Sem descrição')[:300]}")
            lines.append(f"    URL: {r.get('href', '')}")
        return "\n".join(lines)
    except Exception as e:
        log.warning(f"Erro na busca web: {e}")
        return f"Erro na busca: {e}"
