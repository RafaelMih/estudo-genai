"""Testes para shared/utils.py."""

import pytest
from shared.utils import clean_text, truncate, chunk_list, format_sources


def test_clean_text_removes_extra_spaces():
    assert clean_text("hello   world") == "hello world"


def test_clean_text_normalizes_newlines():
    result = clean_text("line1\r\nline2\n\n\n\nline3")
    assert "\r\n" not in result
    assert result.count("\n\n") <= 1


def test_truncate_short_text():
    assert truncate("hello", max_chars=100) == "hello"


def test_truncate_long_text():
    result = truncate("a" * 200, max_chars=50)
    assert len(result) <= 50
    assert result.endswith("...")


def test_chunk_list():
    data = list(range(10))
    chunks = chunk_list(data, 3)
    assert len(chunks) == 4
    assert chunks[0] == [0, 1, 2]
    assert chunks[-1] == [9]


def test_format_sources():
    chunks = [
        {"text": "RAG combina busca com geração", "metadata": {"source": "paper.txt"}},
        {"text": "Embeddings são vetores", "metadata": {"source": "tutorial.md"}},
    ]
    result = format_sources(chunks)
    assert "[1]" in result
    assert "paper.txt" in result
    assert "RAG combina" in result
