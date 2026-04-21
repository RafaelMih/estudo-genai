"""Testes para módulo de chunking."""

import pytest
from modules.rag.chunker import fixed_size_chunk, sentence_chunk, recursive_chunk

SAMPLE_TEXT = (
    "RAG significa Retrieval-Augmented Generation. "
    "É uma técnica que combina busca vetorial com geração de texto. "
    "O pipeline tem duas fases: ingestão e consulta. "
    "Na ingestão, documentos são carregados e convertidos em embeddings. "
    "Na consulta, a query é embedada e os chunks similares são recuperados."
)


def test_fixed_size_chunk_basic():
    chunks = fixed_size_chunk(SAMPLE_TEXT, size=100, overlap=10)
    assert len(chunks) > 0
    assert all(isinstance(c, str) for c in chunks)


def test_fixed_size_chunk_overlap():
    chunks = fixed_size_chunk("abcdefghij", size=5, overlap=2)
    assert len(chunks) >= 2
    # Verifica que há overlap entre chunks consecutivos
    if len(chunks) > 1:
        assert chunks[0][-2:] == chunks[1][:2] or len(chunks[1]) <= 2


def test_sentence_chunk_returns_strings():
    chunks = sentence_chunk(SAMPLE_TEXT, max_sentences=2)
    assert len(chunks) > 0
    assert all(isinstance(c, str) for c in chunks)


def test_sentence_chunk_max_sentences():
    # Com max_sentences=1, cada chunk deve ter aproximadamente 1 sentença
    chunks = sentence_chunk(SAMPLE_TEXT, max_sentences=1)
    assert len(chunks) >= 3


def test_recursive_chunk_basic():
    chunks = recursive_chunk(SAMPLE_TEXT, max_size=150, overlap=20)
    assert len(chunks) > 0
    assert all(isinstance(c, str) and len(c) > 0 for c in chunks)


def test_empty_text():
    assert fixed_size_chunk("", size=100) == []
    assert sentence_chunk("") == []
