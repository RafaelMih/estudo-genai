"""Métricas semânticas: similaridade de embedding e BERTScore."""

from __future__ import annotations

from modules.embeddings.local_embedder import LocalEmbedder
from modules.embeddings.similarity import cosine_similarity
from shared.logger import get_logger

log = get_logger(__name__)

_embedder: LocalEmbedder | None = None


def get_embedder() -> LocalEmbedder:
    global _embedder
    if _embedder is None:
        _embedder = LocalEmbedder()
    return _embedder


def embedding_similarity(text1: str, text2: str) -> float:
    """Similaridade cosseno entre embeddings de dois textos."""
    emb = get_embedder()
    v1 = emb.embed_one(text1)
    v2 = emb.embed_one(text2)
    return round(cosine_similarity(v1, v2), 4)


def bert_score_f1(predictions: list[str], references: list[str], lang: str = "pt") -> list[float]:
    """Calcula BERTScore F1 para listas de prediction/reference."""
    try:
        from bert_score import score as _bert_score
        _, _, F = _bert_score(predictions, references, lang=lang, verbose=False)
        return [round(float(f), 4) for f in F]
    except ImportError:
        log.warning("bert-score não instalado. Usando embedding_similarity como fallback.")
        return [embedding_similarity(p, r) for p, r in zip(predictions, references)]


if __name__ == "__main__":
    pairs = [
        ("RAG combina busca com geração", "Retrieval-Augmented Generation usa recuperação"),
        ("RAG combina busca com geração", "Python é uma linguagem de programação"),
    ]
    print("SIMILARIDADE SEMÂNTICA (embedding cosseno):")
    for a, b in pairs:
        sim = embedding_similarity(a, b)
        print(f"  {sim:.4f}  |  '{a}' ↔ '{b}'")
