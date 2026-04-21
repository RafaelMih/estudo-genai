"""Agente ReAct: Reasoning + Acting loop implementado do zero."""

from __future__ import annotations

import re
from typing import Callable

from modules.agents.tools.calculator import calculator
from modules.agents.tools.file_reader import file_reader
from modules.agents.tools.web_search import web_search
from modules.agents.memory.short_term import ShortTermMemory
from shared.llm_client import build_client
from shared.llm_interface import LLM
from shared.logger import get_logger

log = get_logger(__name__)

TOOL_REGISTRY: dict[str, Callable] = {
    "web_search": web_search,
    "calculator": calculator,
    "file_reader": file_reader,
}

REACT_SYSTEM = """Você é um agente que resolve problemas usando ferramentas. Para cada passo, use EXATAMENTE este formato:

Thought: [seu raciocínio sobre o que fazer]
Action: nome_da_ferramenta(argumento)

Quando tiver a resposta final:
Thought: Tenho todas as informações necessárias.
Final Answer: [resposta completa para o usuário]

Ferramentas disponíveis:
- web_search(query) — busca na web
- calculator(expression) — avalia expressões matemáticas
- file_reader(path) — lê arquivo local

Regras:
- SEMPRE use o formato exato acima
- NUNCA invente resultados — use as ferramentas para buscá-los
- Máximo de 8 passos
"""


class ReActAgent:
    def __init__(
        self,
        max_steps: int = 8,
        client: LLM | None = None,
        memory: ShortTermMemory | None = None,
        tool_registry: dict[str, Callable[[str], str]] | None = None,
    ) -> None:
        self._client = client or build_client()
        self._max_steps = max_steps
        self._memory = memory or ShortTermMemory(max_messages=30)
        self._tool_registry = tool_registry or TOOL_REGISTRY

    def _parse_action(self, text: str) -> tuple[str, str] | None:
        match = re.search(r"Action:\s*(\w+)\((.+?)\)\s*$", text, re.MULTILINE)
        if not match:
            return None
        return match.group(1), match.group(2).strip().strip("\"'")

    def _parse_final(self, text: str) -> str | None:
        match = re.search(r"Final Answer:\s*(.+)", text, re.DOTALL)
        return match.group(1).strip() if match else None

    def run(self, query: str) -> str:
        self._memory.clear()
        self._memory.add("user", query)

        for step in range(self._max_steps):
            log.info(f"[ReAct step {step + 1}/{self._max_steps}]")
            messages = self._memory.get_messages()
            response = self._client.complete(messages, system=REACT_SYSTEM, max_tokens=1024)
            log.debug(f"LLM output:\n{response}")
            self._memory.add("assistant", response)

            final = self._parse_final(response)
            if final:
                return final

            action = self._parse_action(response)
            if action:
                tool_name, tool_arg = action
                if tool_name in self._tool_registry:
                    log.info(f"  → {tool_name}({tool_arg[:60]})")
                    observation = self._tool_registry[tool_name](tool_arg)
                    obs_msg = f"Observation: {observation[:500]}"
                    self._memory.add("user", obs_msg)
                else:
                    self._memory.add(
                        "user",
                        f"Observation: Tool '{tool_name}' não existe. Use: {list(self._tool_registry)}",
                    )
            else:
                # Sem action nem final answer — pede ao modelo para continuar
                self._memory.add("user", "Continue com o próximo passo usando o formato correto.")

        return "Não consegui completar a tarefa dentro do limite de passos."


def main() -> None:
    agent = ReActAgent()
    query = "Quanto é 15% de 2.450? E qual é a raiz quadrada desse valor?"
    print(f"\nQuery: {query}\n")
    result = agent.run(query)
    print(f"\nResposta final: {result}")


if __name__ == "__main__":
    main()
