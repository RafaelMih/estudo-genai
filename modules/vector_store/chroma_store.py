"""ChromaDB wrapper — implementa VectorStore usando embeddings externos (desacoplado do embedder)."""

from __future__ import annotations

import uuid
from pathlib import Path

import chromadb
from chromadb.config import Settings as ChromaSettings

from shared.config import settings as app_settings
from shared.logger import get_logger

log = get_logger(__name__)


class ChromaVectorStore:
    def __init__(self, collection_name: str = "default", persist_dir: str | None = None) -> None:
        dir_path = persist_dir or app_settings.chroma_persist_dir
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(
            path=dir_path,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        log.info(f"ChromaDB collection '{collection_name}' carregada ({self._collection.count()} docs)")

    def add(
        self,
        texts: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict],
        ids: list[str] | None = None,
    ) -> None:
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in texts]
        self._collection.add(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids,
        )
        log.info(f"Adicionados {len(texts)} documentos. Total: {self._collection.count()}")

    def query(
        self,
        query_embedding: list[float],
        n_results: int = 5,
        where: dict | None = None,
    ) -> list[dict]:
        kwargs: dict = {
            "query_embeddings": [query_embedding],
            "n_results": min(n_results, self._collection.count() or 1),
            "include": ["documents", "metadatas", "distances"],
        }
        if where:
            kwargs["where"] = where

        result = self._collection.query(**kwargs)
        docs = result["documents"][0]
        metas = result["metadatas"][0]
        distances = result["distances"][0]

        return [
            {"text": doc, "metadata": meta, "score": 1 - dist}
            for doc, meta, dist in zip(docs, metas, distances)
        ]

    def delete(self, ids: list[str]) -> None:
        self._collection.delete(ids=ids)
        log.info(f"Deletados {len(ids)} documentos.")

    def count(self) -> int:
        return self._collection.count()

    def get_collection_stats(self) -> dict:
        return {
            "name": self._collection.name,
            "count": self._collection.count(),
            "metadata": self._collection.metadata,
        }

    def reset(self) -> None:
        self._client.delete_collection(self._collection.name)
        self._collection = self._client.get_or_create_collection(
            name=self._collection.name,
            metadata={"hnsw:space": "cosine"},
        )
        log.warning(f"Collection '{self._collection.name}' resetada.")


def main() -> None:
    from modules.embeddings.local_embedder import LocalEmbedder

    embedder = LocalEmbedder()
    store = ChromaVectorStore(collection_name="demo", persist_dir="./demo_chroma_db")
    store.reset()

    docs = [
        ("RAG combina busca vetorial com geração de texto", {"source": "paper", "topic": "RAG"}),
        ("ChromaDB é um banco de dados vetorial open-source", {"source": "docs", "topic": "vectordb"}),
        ("Embeddings representam texto como vetores numéricos", {"source": "tutorial", "topic": "embeddings"}),
        ("Transformers usam mecanismo de atenção", {"source": "paper", "topic": "LLM"}),
        ("Python é amplamente usado em machine learning", {"source": "blog", "topic": "python"}),
    ]

    texts = [d[0] for d in docs]
    metas = [d[1] for d in docs]
    embeddings = embedder.embed_batch(texts)
    store.add(texts, embeddings, metas)

    query = "Como funciona a busca semântica?"
    q_vec = embedder.embed_one(query)
    results = store.query(q_vec, n_results=3)

    print(f"\nQuery: '{query}'\n")
    for r in results:
        print(f"  [{r['score']:.3f}] {r['text'][:60]}  (source: {r['metadata']['source']})")

    print(f"\nEstatísticas: {store.get_collection_stats()}")


if __name__ == "__main__":
    main()
