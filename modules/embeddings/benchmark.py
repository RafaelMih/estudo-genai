"""Compara diferentes modelos de embedding em velocidade e qualidade."""

from __future__ import annotations

import time
import numpy as np

from modules.embeddings.local_embedder import LocalEmbedder
from modules.embeddings.similarity import cosine_similarity
from shared.logger import get_logger

log = get_logger(__name__)

MODELS = ["all-MiniLM-L6-v2", "all-mpnet-base-v2", "paraphrase-multilingual-MiniLM-L12-v2"]

TEST_PAIRS = [
    ("RAG usa busca vetorial", "Retrieval-Augmented Generation combina recuperação com LLMs", 0.9),
    ("Python é uma linguagem", "Java é uma linguagem de programação", 0.7),
    ("O gato dormiu", "A nave decolou para Marte", 0.1),
]


def benchmark_model(model_name: str) -> dict:
    log.info(f"Testando modelo: {model_name}")
    embedder = LocalEmbedder(model_name)

    corpus = [pair[0] for pair in TEST_PAIRS] + [pair[1] for pair in TEST_PAIRS]
    start = time.perf_counter()
    embedder.embed_batch(corpus)
    elapsed = time.perf_counter() - start

    similarities = []
    for a, b, _ in TEST_PAIRS:
        va = embedder.embed_one(a)
        vb = embedder.embed_one(b)
        similarities.append(cosine_similarity(va, vb))

    return {
        "model": model_name,
        "dimension": embedder.dimension,
        "time_s": round(elapsed, 3),
        "similarities": [round(s, 4) for s in similarities],
    }


def main() -> None:
    print("\nBENCHMARK DE MODELOS DE EMBEDDING\n")
    print(f"{'Modelo':<45} {'Dim':>5} {'Tempo':>8}  Similaridades")
    print("-" * 90)

    for model_name in MODELS:
        result = benchmark_model(model_name)
        sims = "  ".join(f"{s:.3f}" for s in result["similarities"])
        print(f"{result['model']:<45} {result['dimension']:>5} {result['time_s']:>6.2f}s  {sims}")

    print("\nPares testados:")
    for i, (a, b, expected) in enumerate(TEST_PAIRS, 1):
        print(f"  [{i}] '{a}' ↔ '{b}' (esperado: {'alto' if expected > 0.7 else 'baixo' if expected < 0.3 else 'médio'})")


if __name__ == "__main__":
    main()
