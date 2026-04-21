"""Re-ranking de chunks recuperados usando cross-encoder."""

from __future__ import annotations

from shared.logger import get_logger

log = get_logger(__name__)


class CrossEncoderReranker:
    """Re-ranker que usa cross-encoder para pontuação mais precisa que bi-encoder."""

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2") -> None:
        from sentence_transformers import CrossEncoder
        log.info(f"Carregando cross-encoder: {model_name}")
        self._model = CrossEncoder(model_name)

    def rerank(self, query: str, chunks: list[dict], top_k: int | None = None) -> list[dict]:
        if not chunks:
            return chunks
        texts = [c["text"] for c in chunks]
        pairs = [(query, text) for text in texts]
        scores = self._model.predict(pairs)
        reranked = sorted(
            zip(chunks, scores),
            key=lambda x: x[1],
            reverse=True,
        )
        result = [
            {**chunk, "rerank_score": float(score)}
            for chunk, score in reranked
        ]
        return result[:top_k] if top_k else result


if __name__ == "__main__":
    sample_chunks = [
        {"text": "RAG combina busca vetorial com LLMs para gerar respostas baseadas em documentos.", "score": 0.8},
        {"text": "Python é uma linguagem de programação popular.", "score": 0.7},
        {"text": "A recuperação aumentada por geração melhora a precisão dos modelos de linguagem.", "score": 0.75},
    ]
    reranker = CrossEncoderReranker()
    results = reranker.rerank("O que é RAG?", sample_chunks, top_k=2)
    print("\nRe-ranked results:")
    for r in results:
        print(f"  rerank={r['rerank_score']:.4f}  retrieval={r['score']:.3f}  {r['text'][:70]}")
