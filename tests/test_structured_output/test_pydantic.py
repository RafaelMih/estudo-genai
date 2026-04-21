"""Testes Story 02 — pydantic_output.py"""

import json

import pytest
from pydantic import BaseModel

from modules.structured_output.pydantic_output import PydanticOutputParser, build_output_parser
from shared.llm_interface import TextBlock, ToolResponse, ToolUseBlock


class _Concept(BaseModel):
    name: str
    year: int | None = None
    tags: list[str] = []


@pytest.fixture
def parser(mock_llm_client):
    mock_llm_client.complete.return_value = json.dumps(
        {"name": "Transformer", "year": 2017, "tags": ["attention", "nlp"]}
    )
    return build_output_parser(_Concept, mock_llm_client)


def test_parse_returns_pydantic_instance(parser):
    result = parser.parse("qualquer texto")
    assert isinstance(result, _Concept)
    assert result.name == "Transformer"
    assert result.year == 2017


def test_parse_validates_types(mock_llm_client):
    mock_llm_client.complete.return_value = json.dumps({"name": "X", "year": "nao_e_int"})
    parser = build_output_parser(_Concept, mock_llm_client)
    with pytest.raises(Exception):
        parser.parse("texto")


def test_parse_raises_on_malformed_json(mock_llm_client):
    mock_llm_client.complete.return_value = "não é json"
    parser = build_output_parser(_Concept, mock_llm_client)
    with pytest.raises(ValueError, match="JSON inválido"):
        parser.parse("texto")


def test_parse_tool_response(mock_llm_client):
    tool_block = ToolUseBlock(
        type="tool_use",
        id="t1",
        name="extract",
        input={"name": "BERT", "year": 2018, "tags": ["bert"]},
    )
    response = ToolResponse(stop_reason="tool_use", content=[tool_block])
    parser = build_output_parser(_Concept, mock_llm_client)
    result = parser.parse_tool_response(response)
    assert isinstance(result, _Concept)
    assert result.name == "BERT"


def test_parse_tool_response_raises_without_tool_block(mock_llm_client):
    text_response = ToolResponse(
        stop_reason="end_turn",
        content=[TextBlock(type="text", text="olá")],
    )
    parser = build_output_parser(_Concept, mock_llm_client)
    with pytest.raises(ValueError, match="ToolUseBlock"):
        parser.parse_tool_response(text_response)


def test_build_output_parser_returns_parser(mock_llm_client):
    parser = build_output_parser(_Concept, mock_llm_client)
    assert isinstance(parser, PydanticOutputParser)
    assert parser.schema is _Concept
