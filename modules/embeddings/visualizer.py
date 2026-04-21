"""Visualiza clusters de embeddings com t-SNE e PCA usando matplotlib."""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA

from modules.embeddings.local_embedder import LocalEmbedder
from shared.logger import get_logger

log = get_logger(__name__)

SAMPLE_DATA = {
    "IA & ML": [
        "Redes neurais aprendem com dados",
        "Transformers usam atenção para processar texto",
        "Embeddings são representações vetoriais",
        "RAG combina busca com geração de texto",
        "Modelos de linguagem predizem próximos tokens",
    ],
    "Programação": [
        "Python é uma linguagem interpretada",
        "JavaScript roda no navegador",
        "SQL é usado para consultar bancos de dados",
        "Git controla versões de código",
        "Docker containeriza aplicações",
    ],
    "Culinária": [
        "O risoto precisa de caldo quente",
        "Pão fermenta com levedura",
        "Massa fresca leva ovos e farinha",
        "O churrasco usa brasa de carvão",
        "Sorvete é feito com creme e açúcar",
    ],
}


def plot_embeddings(output_path: str = "embedding_clusters.png", method: str = "tsne") -> None:
    embedder = LocalEmbedder()

    texts, labels, colors_map = [], [], {}
    color_list = ["#e74c3c", "#3498db", "#2ecc71"]
    for i, (category, phrases) in enumerate(SAMPLE_DATA.items()):
        texts.extend(phrases)
        labels.extend([category] * len(phrases))
        colors_map[category] = color_list[i]

    log.info(f"Gerando embeddings para {len(texts)} textos...")
    vectors = np.array(embedder.embed_batch(texts))

    log.info(f"Reduzindo dimensionalidade com {method.upper()}...")
    if method == "tsne":
        reducer = TSNE(n_components=2, perplexity=5, random_state=42)
    else:
        reducer = PCA(n_components=2, random_state=42)
    coords = reducer.fit_transform(vectors)

    plt.figure(figsize=(10, 7))
    for category in SAMPLE_DATA:
        mask = [l == category for l in labels]
        x = coords[mask, 0]
        y = coords[mask, 1]
        plt.scatter(x, y, c=colors_map[category], label=category, s=120, alpha=0.8)
        for xi, yi, text in zip(x, y, [t for t, l in zip(texts, labels) if l == category]):
            plt.annotate(text[:30], (xi, yi), fontsize=7, alpha=0.7, xytext=(4, 4), textcoords="offset points")

    plt.title(f"Clusters de Embedding ({method.upper()}) — modelo: {embedder.model_name}")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    log.info(f"Plot salvo em: {output_path}")
    plt.show()


def main() -> None:
    plot_embeddings(method="tsne")


if __name__ == "__main__":
    main()
