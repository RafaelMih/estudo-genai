"""Busca chunks relevantes no vector store dado uma query."""

from __future__ import annotations

from modules.embeddings.embedder import Embedder
from modules.embeddings.local_embedder import LocalEmbedder
from modules.vector_store.chroma_store import ChromaVectorStore
from modules.vector_store.store_interface import VectorStore
from shared.logger import get_logger

log = get_logger(__name__)


class Retriever:
    def __init__(self, store: VectorStore | ChromaVectorStore, embedder: Embedder | None = None) -> None:
        self._store = store
        self._embedder = embedder or LocalEmbedder()

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.0,
        where: dict | None = None,
    ) -> list[dict]:
        query_vec = self._embedder.embed_one(query)
        results = self._store.query(query_vec, n_results=top_k, where=where)
        filtered = [r for r in results if r["score"] >= score_threshold]
        log.info(f"Recuperados {len(filtered)} chunks para: '{query[:60]}'")
        return filtered
