"""CLI: responde uma pergunta usando o pipeline RAG."""

import argparse

from modules.rag.pipeline import RAGPipeline
from shared.llm_client import ANTHROPIC_PROVIDER, OPENAI_PROVIDER, build_client
from shared.logger import get_logger

log = get_logger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="Responde perguntas usando RAG")
    parser.add_argument("--question", required=True, help="Pergunta a ser respondida")
    parser.add_argument("--collection", default="rag_docs", help="Collection ChromaDB a usar")
    parser.add_argument("--top-k", type=int, default=5, help="Número de chunks a recuperar")
    parser.add_argument("--show-sources", action="store_true", help="Mostrar chunks recuperados")
    parser.add_argument("--provider", choices=[ANTHROPIC_PROVIDER, OPENAI_PROVIDER], help="Provider LLM")
    parser.add_argument("--model", help="Modelo LLM")
    args = parser.parse_args()

    pipeline = RAGPipeline(
        collection_name=args.collection,
        top_k=args.top_k,
        llm=build_client(provider=args.provider, model=args.model),
    )
    result = pipeline.query(args.question)

    print(f"\nQ: {result['question']}")
    print(f"\nA: {result['answer']}")

    if args.show_sources and result["sources"]:
        print(f"\n--- Fontes recuperadas ({len(result['sources'])}) ---")
        for i, s in enumerate(result["sources"], 1):
            print(f"[{i}] score={s['score']:.3f} | {s['metadata'].get('source', '?')} | {s['text'][:100]}...")


if __name__ == "__main__":
    main()
