"""Self-Consistency: amostra N respostas e retorna a resposta por majority vote."""

from __future__ import annotations

import re
from collections import Counter

from shared.llm_client import build_client
from shared.logger import get_logger

log = get_logger(__name__)


def extract_final_answer(text: str) -> str:
    """Extrai a resposta numérica ou palavra-chave final do texto de CoT."""
    # Tenta encontrar número no final
    numbers = re.findall(r"\b\d+(?:[.,]\d+)?\b", text)
    return numbers[-1] if numbers else text.strip().split("\n")[-1].strip()[:50]


def self_consistency(question: str, n_samples: int = 5, temperature: float = 0.8) -> dict:
    """Amostra N respostas com CoT e retorna a mais frequente."""
    client = build_client()
    cot_question = question + "\n\nVamos pensar passo a passo."
    messages = [{"role": "user", "content": cot_question}]

    answers = []
    full_responses = []

    log.info(f"Gerando {n_samples} amostras com temperature={temperature}...")
    for i in range(n_samples):
        response = client.complete(messages, temperature=temperature, max_tokens=512)
        full_responses.append(response)
        answer = extract_final_answer(response)
        answers.append(answer)
        log.debug(f"  Sample {i+1}: {answer}")

    counter = Counter(answers)
    most_common, votes = counter.most_common(1)[0]
    confidence = votes / n_samples

    return {
        "final_answer": most_common,
        "confidence": confidence,
        "votes": votes,
        "n_samples": n_samples,
        "all_answers": answers,
        "full_responses": full_responses,
    }


def main() -> None:
    question = "Uma loja tem 120 produtos. Vende 45% na segunda e 30% do restante na terça. Quantos produtos restam?"

    print(f"Pergunta: {question}\n")
    result = self_consistency(question, n_samples=5)

    print(f"Resposta final (majority vote): {result['final_answer']}")
    print(f"Confiança: {result['confidence']:.0%} ({result['votes']}/{result['n_samples']} amostras concordam)")
    print(f"\nTodas as respostas extraídas: {result['all_answers']}")


if __name__ == "__main__":
    main()
