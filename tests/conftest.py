"""Fixtures compartilhados para todos os testes."""

import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_llm_client():
    """LLM client mockado — sem chamadas à API."""
    with patch("shared.llm_client.build_client") as mock_build:
        client = MagicMock()
        client.complete.return_value = "Resposta mockada do LLM."
        client.count_tokens.return_value = 42
        mock_build.return_value = client
        yield client


@pytest.fixture
def mock_embedder():
    """Embedder mockado que retorna vetores determinísticos."""
    embedder = MagicMock()
    embedder.dimension = 384
    embedder.embed_one.return_value = [0.1] * 384
    embedder.embed_batch.side_effect = lambda texts, **_: [[0.1] * 384] * len(texts)
    return embedder


@pytest.fixture
def in_memory_chroma():
    """ChromaDB em memória para testes — sem persistência em disco."""
    import chromadb
    from chromadb.config import Settings
    client = chromadb.Client(Settings(is_persistent=False, anonymized_telemetry=False))
    collection = client.get_or_create_collection("test", metadata={"hnsw:space": "cosine"})
    yield collection
    client.delete_collection("test")
