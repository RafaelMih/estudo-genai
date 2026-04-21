"""Métricas de similaridade entre vetores de embedding."""

from __future__ import annotations

import math
import numpy as np

from modules.embeddings.local_embedder import LocalEmbedder
from shared.logger import get_logger

log = get_logger(__name__)


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Similaridade cosseno entre dois vetores. Resultado em [-1, 1]."""
    va, vb = np.array(a), np.array(b)
    denom = np.linalg.norm(va) * np.linalg.norm(vb)
    return float(np.dot(va, vb) / denom) if denom > 0 else 0.0


def dot_product(a: list[float], b: list[float]) -> float:
    """Produto interno — equivalente ao cosseno quando vetores são normalizados."""
    return float(np.dot(a, b))


def euclidean_distance(a: list[float], b: list[float]) -> float:
    """Distância euclidiana. Menor = mais similar."""
    return float(np.linalg.norm(np.array(a) - np.array(b)))


def semantic_search(query: str, corpus: list[str], embedder: LocalEmbedder, top_k: int = 5) -> list[dict]:
    """Busca semântica: retorna os top-k textos mais similares à query."""
    query_vec = embedder.embed_one(query)
    corpus_vecs = embedder.embed_batch(corpus)
    scores = [(cosine_similarity(query_vec, vec), text) for vec, text in zip(corpus_vecs, corpus)]
    scores.sort(key=lambda x: x[0], reverse=True)
    return [{"score": s, "text": t} for s, t in scores[:top_k]]


def main() -> None:
    embedder = LocalEmbedder()

    pairs = [
        ("RAG é uma técnica de IA", "Retrieval-Augmented Generation combina busca com LLMs"),
        ("RAG é uma técnica de IA", "Python é uma linguagem de programação"),
        ("O cachorro latiu", "O cão fez barulho"),
        ("O cachorro latiu", "A nave espacial decolou"),
    ]

    print("\nSIMILARIDADE COSSENO ENTRE PARES:\n")
    for a, b in pairs:
        va = embedder.embed_one(a)
        vb = embedder.embed_one(b)
        sim = cosine_similarity(va, vb)
        print(f"  {sim:.4f}  |  '{a[:40]}' ↔ '{b[:40]}'")

    print("\n\nBUSCA SEMÂNTICA:")
    corpus = [
        "RAG combina recuperação de documentos com geração de texto",
        "Python foi criado por Guido van Rossum",
        "ChromaDB é um banco de dados vetorial",
        "Transformers usam mecanismo de atenção",
        "Embeddings representam texto como vetores numéricos",
        "Redes neurais têm camadas de neurônios artificiais",
    ]
    query = "Como funciona a busca em bancos de dados vetoriais?"
    results = semantic_search(query, corpus, embedder, top_k=3)
    print(f"\nQuery: '{query}'")
    print("Top 3 resultados:")
    for r in results:
        print(f"  {r['score']:.4f}  {r['text']}")


if __name__ == "__main__":
    main()
