"""Demonstra filtros de metadados no ChromaDB (where clauses)."""

from modules.embeddings.local_embedder import LocalEmbedder
from modules.vector_store.chroma_store import ChromaVectorStore
from shared.logger import get_logger

log = get_logger(__name__)

SAMPLE_DOCS = [
    ("RAG usa busca vetorial", {"source": "paper", "year": 2020, "topic": "RAG"}),
    ("ChromaDB suporta filtros de metadados", {"source": "docs", "year": 2023, "topic": "vectordb"}),
    ("Embeddings locais com sentence-transformers", {"source": "tutorial", "year": 2022, "topic": "embeddings"}),
    ("Transformers revolucionaram o NLP", {"source": "paper", "year": 2017, "topic": "LLM"}),
    ("LLMs como GPT e Claude são grandes modelos", {"source": "blog", "year": 2023, "topic": "LLM"}),
    ("FAISS é uma biblioteca de busca vetorial", {"source": "docs", "year": 2021, "topic": "vectordb"}),
]


def demo() -> None:
    embedder = LocalEmbedder()
    store = ChromaVectorStore(collection_name="filter_demo", persist_dir="./demo_chroma_db")
    store.reset()

    texts = [d[0] for d in SAMPLE_DOCS]
    metas = [d[1] for d in SAMPLE_DOCS]
    store.add(texts, embedder.embed_batch(texts), metas)

    query = "busca e recuperação de informações"
    q_vec = embedder.embed_one(query)

    print("=" * 60)
    print("1. SEM FILTRO (todos os documentos)")
    print("=" * 60)
    for r in store.query(q_vec, n_results=3):
        print(f"  [{r['score']:.3f}] {r['text']} ({r['metadata']})")

    print("\n" + "=" * 60)
    print('2. FILTRO: source == "paper"')
    print("=" * 60)
    for r in store.query(q_vec, n_results=3, where={"source": "paper"}):
        print(f"  [{r['score']:.3f}] {r['text']}")

    print("\n" + "=" * 60)
    print("3. FILTRO: year >= 2022")
    print("=" * 60)
    for r in store.query(q_vec, n_results=3, where={"year": {"$gte": 2022}}):
        print(f"  [{r['score']:.3f}] {r['text']} (year: {r['metadata']['year']})")

    print("\n" + "=" * 60)
    print('4. FILTRO: topic == "vectordb" OR topic == "RAG"')
    print("=" * 60)
    where = {"$or": [{"topic": "vectordb"}, {"topic": "RAG"}]}
    for r in store.query(q_vec, n_results=5, where=where):
        print(f"  [{r['score']:.3f}] {r['text']} (topic: {r['metadata']['topic']})")


if __name__ == "__main__":
    demo()
