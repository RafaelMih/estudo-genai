"""Construção e formatação de exemplos few-shot."""

from __future__ import annotations

from dataclasses import dataclass

from shared.llm_client import build_client


@dataclass
class Example:
    input: str
    output: str


class FewShotPrompt:
    def __init__(self, task_description: str, examples: list[Example]) -> None:
        self._task = task_description
        self._examples = examples
        self._client = build_client()

    def _build_prompt(self, query: str) -> str:
        lines = [self._task, ""]
        for ex in self._examples:
            lines.append(f"Input: {ex.input}")
            lines.append(f"Output: {ex.output}")
            lines.append("")
        lines.append(f"Input: {query}")
        lines.append("Output:")
        return "\n".join(lines)

    def run(self, query: str) -> str:
        messages = [{"role": "user", "content": self._build_prompt(query)}]
        return self._client.complete(messages, max_tokens=256)


SENTIMENT_EXAMPLES = [
    Example("Esse produto é incrível, adorei!", "positivo"),
    Example("Péssima qualidade, não recomendo.", "negativo"),
    Example("O produto chegou no prazo.", "neutro"),
    Example("Simplesmente perfeito para o que precisava!", "positivo"),
]

if __name__ == "__main__":
    prompt = FewShotPrompt(
        task_description="Classifique o sentimento da avaliação como: positivo, negativo ou neutro.",
        examples=SENTIMENT_EXAMPLES,
    )
    tests = [
        "Fui mal atendido e o produto veio com defeito.",
        "Entrega rápida e produto conforme descrito.",
        "Superou minhas expectativas! Já comprei mais vezes.",
    ]
    for text in tests:
        result = prompt.run(text)
        print(f"'{text}' → {result.strip()}")
