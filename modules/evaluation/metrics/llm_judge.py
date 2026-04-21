"""LLM-as-judge: usa Claude para avaliar respostas com rubrica estruturada."""

from __future__ import annotations

import json
import re

from shared.llm_client import build_client
from shared.logger import get_logger

log = get_logger(__name__)

JUDGE_SYSTEM = """Você é um avaliador especializado em qualidade de respostas de IA.
Avalie a resposta com base nos critérios fornecidos usando uma escala de 1-5.
Responda APENAS em JSON válido com o formato exato:
{"faithfulness": N, "relevance": N, "coherence": N, "reasoning": "..."}

Critérios:
- faithfulness (1-5): A resposta se baseia no contexto sem inventar informações? (5=perfeito, 1=muita alucinação)
- relevance (1-5): A resposta responde à pergunta de forma direta? (5=muito relevante, 1=irrelevante)
- coherence (1-5): A resposta é clara e bem estruturada? (5=excelente, 1=confusa)
- reasoning: Uma frase explicando os scores"""


class LLMJudge:
    def __init__(self) -> None:
        self._client = build_client()

    def evaluate(self, question: str, answer: str, context: str = "") -> dict:
        prompt = f"""PERGUNTA: {question}

CONTEXTO FORNECIDO AO SISTEMA:
{context[:1000] if context else "(sem contexto)"}

RESPOSTA DO SISTEMA:
{answer[:1000]}

Avalie a resposta acima."""

        messages = [{"role": "user", "content": prompt}]
        raw = self._client.complete(messages, system=JUDGE_SYSTEM, max_tokens=300)

        try:
            raw = raw.strip().removeprefix("```json").removesuffix("```").strip()
            result = json.loads(raw)
        except json.JSONDecodeError:
            numbers = re.findall(r"\b[1-5]\b", raw)
            result = {
                "faithfulness": int(numbers[0]) if len(numbers) > 0 else 3,
                "relevance": int(numbers[1]) if len(numbers) > 1 else 3,
                "coherence": int(numbers[2]) if len(numbers) > 2 else 3,
                "reasoning": "Parse error — scores extraídos por regex",
            }

        result["overall"] = round(
            (result.get("faithfulness", 3) + result.get("relevance", 3) + result.get("coherence", 3)) / 3, 2
        )
        return result


if __name__ == "__main__":
    judge = LLMJudge()
    result = judge.evaluate(
        question="O que é RAG?",
        answer="RAG é uma técnica que combina busca vetorial com geração de texto para produzir respostas baseadas em documentos.",
        context="RAG significa Retrieval-Augmented Generation. Combina recuperação de documentos com modelos de linguagem.",
    )
    print(f"Avaliação: {json.dumps(result, ensure_ascii=False, indent=2)}")
