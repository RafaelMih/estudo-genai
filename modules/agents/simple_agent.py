"""Agente simples usando tool calling nativo do Anthropic SDK (single-step)."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from modules.agents.tools.calculator import TOOL_DEFINITION as CALC_DEF, calculator
from modules.agents.tools.web_search import TOOL_DEFINITION as SEARCH_DEF, web_search
from shared.llm_client import build_client
from shared.llm_interface import LLM
from shared.logger import get_logger

log = get_logger(__name__)

TOOLS = [CALC_DEF, SEARCH_DEF]
TOOL_FUNCTIONS = {"calculator": calculator, "web_search": web_search}

SYSTEM = "Você é um assistente útil com acesso a ferramentas. Use-as quando necessário para responder com precisão."


class SimpleAgent:
    """Agente single-step: LLM decide qual tool chamar, executa uma vez, responde."""

    def __init__(
        self,
        client: LLM | None = None,
        tools: list[dict[str, Any]] | None = None,
        tool_functions: dict[str, Callable[..., str]] | None = None,
    ) -> None:
        self._client = client or build_client()
        self._tools = tools or TOOLS
        self._tool_functions = tool_functions or TOOL_FUNCTIONS

    def run(self, query: str) -> str:
        messages = [{"role": "user", "content": query}]

        # Primeira chamada: LLM decide se usa tool
        response = self._client.complete_with_tools(messages, self._tools, system=SYSTEM)

        if response.stop_reason == "end_turn":
            return response.content[0].text

        # Processa tool use
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                log.info(f"Chamando tool: {block.name}({json.dumps(block.input)[:100]})")
                result = self._tool_functions[block.name](**block.input)
                tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": result})

        # Segunda chamada: LLM gera resposta final com resultados das tools
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})
        final = self._client.complete_with_tools(messages, self._tools, system=SYSTEM)
        return final.content[0].text


def main() -> None:
    agent = SimpleAgent()
    queries = [
        "Quanto é 1234 * 5678?",
        "Qual é a capital da Austrália?",
    ]
    for q in queries:
        print(f"\nQ: {q}")
        print(f"A: {agent.run(q)}")


if __name__ == "__main__":
    main()
