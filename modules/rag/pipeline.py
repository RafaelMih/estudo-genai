"""Pipeline RAG completo: ingestão e consulta."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from modules.embeddings.embedder import Embedder
from modules.embeddings.local_embedder import LocalEmbedder
from modules.prompt_engineering.prompt_library import get_prompt
from modules.rag.chunker import recursive_chunk
from modules.rag.document_loader import load_directory, load_document
from modules.rag.retriever import Retriever
from modules.vector_store.chroma_store import ChromaVectorStore
from modules.vector_store.store_interface import VectorStore
from shared.llm_client import build_client
from shared.llm_interface import LLM
from shared.logger import get_logger

log = get_logger(__name__)

RAG_SYSTEM = (
    "Você é um assistente preciso. Responda baseando-se EXCLUSIVAMENTE nos documentos fornecidos. "
    "Se a informação não estiver nos documentos, diga: 'Não encontrei essa informação nos documentos.'"
)


class RAGPipeline:
    def __init__(
        self,
        collection_name: str = "rag_docs",
        chunk_size: int = 512,
        chunk_overlap: int = 64,
        top_k: int = 5,
        score_threshold: float = 0.3,
        embedder: Embedder | None = None,
        store: VectorStore | None = None,
        retriever: Retriever | None = None,
        llm: LLM | None = None,
        chunker: Callable[[str, int, int], list[str]] = recursive_chunk,
    ) -> None:
        self._embedder = embedder or LocalEmbedder()
        self._store = store or ChromaVectorStore(collection_name=collection_name)
        self._retriever = retriever or Retriever(self._store, self._embedder)
        self._llm = llm or build_client()
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap
        self._top_k = top_k
        self._score_threshold = score_threshold
        self._chunker = chunker

    def ingest(self, path: Path) -> int:
        """Carrega, chunka, embeda e armazena documentos. Retorna nº de chunks indexados."""
        docs = load_directory(path) if path.is_dir() else [load_document(path)]
        total = 0
        for doc in docs:
            chunks = self._chunker(doc["text"], self._chunk_size, self._chunk_overlap)
            embeddings = self._embedder.embed_batch(chunks)
            metadatas = [{**doc["metadata"], "chunk_idx": i} for i in range(len(chunks))]
            self._store.add(chunks, embeddings, metadatas)
            total += len(chunks)
            log.info(f"  {doc['metadata']['source']}: {len(chunks)} chunks indexados")
        log.info(f"Ingestão completa. Total: {total} chunks. Store total: {self._store.count()}")
        return total

    def query(self, question: str) -> dict:
        """Recupera contexto e gera resposta."""
        chunks = self._retriever.retrieve(question, top_k=self._top_k, score_threshold=self._score_threshold)

        if not chunks:
            return {
                "question": question,
                "answer": "Não encontrei documentos relevantes para responder a essa pergunta.",
                "sources": [],
            }

        prompt = get_prompt("rag_answer").render(
            docs=list(enumerate([c["text"] for c in chunks], 1)),
            question=question,
        )
        messages = [{"role": "user", "content": prompt}]
        answer = self._llm.complete(messages, system=RAG_SYSTEM, max_tokens=1024)

        return {
            "question": question,
            "answer": answer,
            "sources": [{"text": c["text"][:100], "score": c["score"], "metadata": c["metadata"]} for c in chunks],
        }

    def reset(self) -> None:
        self._store.reset()


def main() -> None:
    pipeline = RAGPipeline()
    sample_dir = Path("modules/rag/data/sample_docs")

    if sample_dir.exists() and any(sample_dir.iterdir()):
        print("Indexando documentos de exemplo...")
        pipeline.ingest(sample_dir)

        questions = [
            "O que é o mecanismo de atenção em Transformers?",
            "Quais são as vantagens do RAG sobre o fine-tuning?",
        ]
        for q in questions:
            result = pipeline.query(q)
            print(f"\nQ: {result['question']}")
            print(f"A: {result['answer'][:300]}")
            print(f"Fontes: {[s['metadata']['source'] for s in result['sources']]}")
    else:
        print(f"Diretório {sample_dir} vazio. Execute primeiro:")
        print("  python -m scripts.ingest_docs --dir modules/rag/data/sample_docs")


if __name__ == "__main__":
    main()
