"""CLI: carrega documentos, chunkeia, embeda e armazena no ChromaDB."""

import argparse
from pathlib import Path

from modules.rag.pipeline import RAGPipeline
from shared.logger import get_logger

log = get_logger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="Indexa documentos no ChromaDB via pipeline RAG")
    parser.add_argument("--dir", required=True, help="Diretório com documentos a indexar")
    parser.add_argument("--collection", default="rag_docs", help="Nome da collection ChromaDB")
    parser.add_argument("--chunk-size", type=int, default=512, help="Tamanho dos chunks em caracteres")
    parser.add_argument("--reset", action="store_true", help="Resetar collection antes de indexar")
    args = parser.parse_args()

    doc_dir = Path(args.dir)
    if not doc_dir.exists():
        print(f"Diretório não encontrado: {doc_dir}")
        return

    pipeline = RAGPipeline(collection_name=args.collection, chunk_size=args.chunk_size)

    if args.reset:
        log.warning(f"Resetando collection '{args.collection}'...")
        pipeline.reset()

    print(f"Indexando documentos de: {doc_dir}")
    total = pipeline.ingest(doc_dir)
    print(f"\nIndexação concluída: {total} chunks armazenados em '{args.collection}'")
    print("Use: python -m scripts.run_rag_query --question 'Sua pergunta aqui'")


if __name__ == "__main__":
    main()
