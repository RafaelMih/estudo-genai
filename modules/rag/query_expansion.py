"""Técnicas de query expansion: HyDE e multi-query."""

from __future__ import annotations

from shared.llm_client import LLMClient, build_client
from shared.logger import get_logger

log = get_logger(__name__)

HYDE_SYSTEM = """Você é um especialista. Dado uma pergunta, escreva um parágrafo factual e detalhado
que seria a resposta ideal para essa pergunta. Escreva como se fosse um trecho de documentação técnica.
Responda APENAS com o parágrafo, sem introduções."""

MULTI_QUERY_SYSTEM = """Você é um assistente de busca. Dado uma pergunta, gere {{ n }} reformulações
diferentes que capturam o mesmo significado com ângulos distintos.
Responda com uma reformulação por linha, sem numeração ou marcadores."""


def hyde(question: str, client: LLMClient | None = None) -> str:
    """HyDE: gera documento hipotético para ser embedado no lugar da query."""
    client = client or build_client()
    messages = [{"role": "user", "content": f"Pergunta: {question}"}]
    hypothetical_doc = client.complete(messages, system=HYDE_SYSTEM, max_tokens=300)
    log.debug(f"HyDE doc: {hypothetical_doc[:100]}...")
    return hypothetical_doc


def multi_query(question: str, n: int = 3, client: LLMClient | None = None) -> list[str]:
    """Gera N reformulações da query para aumentar recall na busca."""
    client = client or build_client()
    system = MULTI_QUERY_SYSTEM.replace("{{ n }}", str(n))
    messages = [{"role": "user", "content": question}]
    response = client.complete(messages, system=system, max_tokens=300)
    queries = [q.strip() for q in response.strip().split("\n") if q.strip()]
    all_queries = [question] + queries
    log.info(f"Multi-query gerou {len(all_queries)} queries (original + {len(queries)} reformulações)")
    return all_queries


if __name__ == "__main__":
    question = "Como o mecanismo de atenção funciona em Transformers?"

    print("HYDE (Hypothetical Document Embedding):")
    print("-" * 50)
    print(hyde(question))

    print("\n\nMULTI-QUERY EXPANSION:")
    print("-" * 50)
    for q in multi_query(question, n=3):
        print(f"  • {q}")
