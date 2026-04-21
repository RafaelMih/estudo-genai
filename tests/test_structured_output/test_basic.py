"""Testes Story 01 — basic_structured.py"""

import json

import pytest

from modules.structured_output.basic_structured import _strip_markdown_fences, extract_as_json


@pytest.fixture
def llm_returning(mock_llm_client):
    """Helper: configura o mock para retornar um JSON específico."""

    def _configure(payload: dict) -> object:
        mock_llm_client.complete.return_value = json.dumps(payload, ensure_ascii=False)
        return mock_llm_client

    return _configure


def test_extract_returns_dict(llm_returning):
    llm = llm_returning({"nome": "Python", "tipo": "linguagem"})
    result = extract_as_json("texto qualquer", ["nome", "tipo"], llm)
    assert isinstance(result, dict)
    assert result["nome"] == "Python"


def test_extract_calls_complete_once(llm_returning):
    llm = llm_returning({"x": 1})
    extract_as_json("texto", ["x"], llm)
    assert llm.complete.call_count == 1


def test_extract_raises_on_invalid_json(mock_llm_client):
    mock_llm_client.complete.return_value = "isso não é json"
    with pytest.raises(ValueError, match="JSON inválido"):
        extract_as_json("texto", ["campo"], mock_llm_client)


def test_strip_fences_removes_code_block():
    fenced = "```json\n{\"a\": 1}\n```"
    assert _strip_markdown_fences(fenced) == '{"a": 1}'


def test_strip_fences_passthrough_plain():
    plain = '{"a": 1}'
    assert _strip_markdown_fences(plain) == plain
