"""Embedding local usando sentence-transformers (sem chamadas de API, CPU-friendly)."""

from __future__ import annotations

import numpy as np
from sentence_transformers import SentenceTransformer

from shared.config import settings
from shared.logger import get_logger

log = get_logger(__name__)


class LocalEmbedder:
    def __init__(self, model_name: str | None = None) -> None:
        self._model_name = model_name or settings.embedding_model
        log.info(f"Carregando modelo de embedding: {self._model_name}")
        self._model = SentenceTransformer(self._model_name)
        self._dim: int = self._model.get_sentence_embedding_dimension()
        log.info(f"Modelo carregado — dimensão: {self._dim}")

    def embed_one(self, text: str) -> list[float]:
        vector: np.ndarray = self._model.encode(text, normalize_embeddings=True)
        return vector.tolist()

    def embed_batch(self, texts: list[str], batch_size: int = 32) -> list[list[float]]:
        vectors: np.ndarray = self._model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=len(texts) > 100,
        )
        return vectors.tolist()

    @property
    def dimension(self) -> int:
        return self._dim

    @property
    def model_name(self) -> str:
        return self._model_name


def main() -> None:
    embedder = LocalEmbedder()
    phrases = [
        "RAG significa Retrieval-Augmented Generation",
        "Recuperação aumentada por geração de texto",
        "Python é uma linguagem de programação",
        "O gato sentou no tapete",
    ]
    print(f"\nModelo: {embedder.model_name} ({embedder.dimension}D)\n")
    for phrase in phrases:
        vec = embedder.embed_one(phrase)
        print(f"  [{vec[0]:.4f}, {vec[1]:.4f}, ... {vec[-1]:.4f}]  ← '{phrase[:50]}'")


if __name__ == "__main__":
    main()
