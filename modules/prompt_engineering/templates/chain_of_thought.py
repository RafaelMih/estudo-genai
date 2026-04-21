"""Variantes de Chain-of-Thought prompting."""

from shared.llm_client import build_client

ZERO_SHOT_COT_SUFFIX = "\n\nVamos pensar passo a passo."

FEW_SHOT_COT_EXAMPLES = [
    {
        "question": "Roger tem 5 bolas de tênis. Ele compra mais 2 caixas com 3 bolas cada. Quantas bolas ele tem?",
        "reasoning": "Roger começa com 5 bolas.\n2 caixas × 3 bolas = 6 bolas novas.\n5 + 6 = 11 bolas no total.",
        "answer": "11",
    },
    {
        "question": "A cafeteria tinha 23 maçãs. Se usaram 20 para o almoço e compraram mais 6, quantas maçãs têm?",
        "reasoning": "Começaram com 23.\nUsaram 20: 23 - 20 = 3 restantes.\nCompraram 6: 3 + 6 = 9 maçãs.",
        "answer": "9",
    },
]


class ZeroShotCoT:
    """Adiciona 'Vamos pensar passo a passo' ao prompt."""

    def __init__(self) -> None:
        self._client = build_client()

    def solve(self, question: str) -> str:
        prompt = question + ZERO_SHOT_COT_SUFFIX
        messages = [{"role": "user", "content": prompt}]
        return self._client.complete(messages, max_tokens=512)


class FewShotCoT:
    """Fornece exemplos com raciocínio explícito antes da pergunta."""

    def __init__(self) -> None:
        self._client = build_client()

    def _build_prompt(self, question: str) -> str:
        lines = []
        for ex in FEW_SHOT_COT_EXAMPLES:
            lines.append(f"Pergunta: {ex['question']}")
            lines.append(f"Raciocínio: {ex['reasoning']}")
            lines.append(f"Resposta: {ex['answer']}\n")
        lines.append(f"Pergunta: {question}")
        lines.append("Raciocínio:")
        return "\n".join(lines)

    def solve(self, question: str) -> str:
        messages = [{"role": "user", "content": self._build_prompt(question)}]
        return self._client.complete(messages, max_tokens=512)


def main() -> None:
    question = "Uma loja tinha 45 camisetas. Vendeu 18 na segunda e 12 na terça. Quantas restaram?"

    print("=" * 60)
    print("ZERO-SHOT CoT")
    print("=" * 60)
    zs = ZeroShotCoT()
    print(zs.solve(question))

    print("\n" + "=" * 60)
    print("FEW-SHOT CoT")
    print("=" * 60)
    fs = FewShotCoT()
    print(fs.solve(question))


if __name__ == "__main__":
    main()
