"""Demonstra persistência e recarga do ChromaDB do disco."""

import shutil
from pathlib import Path

from modules.embeddings.local_embedder import LocalEmbedder
from modules.vector_store.chroma_store import ChromaVectorStore
from shared.logger import get_logger

log = get_logger(__name__)

PERSIST_DIR = "./demo_persist_chroma"


def demo_persistence() -> None:
    # Limpa e cria fresh
    shutil.rmtree(PERSIST_DIR, ignore_errors=True)

    embedder = LocalEmbedder()

    print("PASSO 1: Criando e populando store...")
    store1 = ChromaVectorStore(collection_name="persist_test", persist_dir=PERSIST_DIR)
    docs = ["RAG combina busca com geração", "Embeddings são vetores", "ChromaDB persiste dados em disco"]
    store1.add(docs, embedder.embed_batch(docs), [{"idx": i} for i in range(len(docs))])
    print(f"  Documentos inseridos: {store1.count()}")
    del store1  # simula encerramento do processo

    print("\nPASSO 2: Recarregando store do disco (novo processo)...")
    store2 = ChromaVectorStore(collection_name="persist_test", persist_dir=PERSIST_DIR)
    print(f"  Documentos recuperados do disco: {store2.count()}")

    q_vec = embedder.embed_one("como buscar documentos por semântica?")
    results = store2.query(q_vec, n_results=2)
    print("\n  Resultados de busca após reload:")
    for r in results:
        print(f"    [{r['score']:.3f}] {r['text']}")

    # Cleanup
    shutil.rmtree(PERSIST_DIR, ignore_errors=True)
    print("\nDemo concluído. Diretório de demo removido.")


if __name__ == "__main__":
    demo_persistence()
