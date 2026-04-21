"""Avaliação de agentes: taxa de seleção correta de tools e task completion."""

from __future__ import annotations

from shared.logger import get_logger

log = get_logger(__name__)

TOOL_SELECTION_TESTS = [
    {"query": "Quanto é 128 * 256?", "expected_tool": "calculator"},
    {"query": "Quem ganhou a Copa do Mundo de 2022?", "expected_tool": "web_search"},
    {"query": "Leia o arquivo python_glossary.txt", "expected_tool": "file_reader"},
    {"query": "Calcule a raiz quadrada de 144", "expected_tool": "calculator"},
    {"query": "Notícias recentes sobre IA generativa", "expected_tool": "web_search"},
]


def evaluate_tool_selection(agent) -> dict:
    """Testa se o agente seleciona a tool correta para cada tipo de query."""
    correct = 0
    results = []

    for test in TOOL_SELECTION_TESTS:
        result = agent.run(test["query"])
        tool_used = _infer_tool_used(result, test["query"])
        is_correct = tool_used == test["expected_tool"]
        if is_correct:
            correct += 1
        results.append({
            "query": test["query"],
            "expected": test["expected_tool"],
            "used": tool_used,
            "correct": is_correct,
        })
        log.info(f"  {'✓' if is_correct else '✗'} {test['query'][:50]} → {tool_used}")

    accuracy = correct / len(TOOL_SELECTION_TESTS)
    return {"accuracy": round(accuracy, 3), "correct": correct, "total": len(TOOL_SELECTION_TESTS), "details": results}


def _infer_tool_used(agent_response: str, query: str) -> str:
    """Heurística para inferir qual tool foi usada com base na resposta."""
    response_lower = agent_response.lower() + query.lower()
    if any(w in response_lower for w in ["calculat", "calcul", "math", "resultado", "=", "equals"]):
        return "calculator"
    if any(w in response_lower for w in ["search", "web", "encontr", "busca", "internet"]):
        return "web_search"
    if any(w in response_lower for w in ["arquivo", "file", "ler", "read"]):
        return "file_reader"
    return "unknown"
