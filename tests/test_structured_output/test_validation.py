"""Testes Story 04 — validation.py (retry + regras de negócio)"""

import json

import pytest
from pydantic import BaseModel

from modules.structured_output.validation import MaxRetriesExceeded, parse_with_retry, validate_output


class _Person(BaseModel):
    name: str
    age: int


def test_parse_with_retry_succeeds_first_attempt(mock_llm_client):
    mock_llm_client.complete.return_value = json.dumps({"name": "Ana", "age": 25})
    result = parse_with_retry("texto", _Person, mock_llm_client, max_retries=3)
    assert result.name == "Ana"
    assert result.age == 25
    assert mock_llm_client.complete.call_count == 1


def test_parse_with_retry_retries_on_failure(mock_llm_client):
    good_payload = json.dumps({"name": "Carlos", "age": 40})
    mock_llm_client.complete.side_effect = ["json ruim", good_payload]
    result = parse_with_retry("texto", _Person, mock_llm_client, max_retries=3)
    assert result.name == "Carlos"
    assert mock_llm_client.complete.call_count == 2


def test_parse_with_retry_raises_after_max_retries(mock_llm_client):
    mock_llm_client.complete.return_value = "sempre inválido"
    with pytest.raises(MaxRetriesExceeded) as exc_info:
        parse_with_retry("texto", _Person, mock_llm_client, max_retries=2)
    assert len(exc_info.value.errors) == 2


def test_parse_with_retry_includes_error_in_retry_prompt(mock_llm_client):
    good_payload = json.dumps({"name": "Bia", "age": 30})
    mock_llm_client.complete.side_effect = ["ruim", good_payload]
    parse_with_retry("texto original", _Person, mock_llm_client, max_retries=3)
    second_call_args = mock_llm_client.complete.call_args_list[1]
    prompt_text = second_call_args[1]["messages"][0]["content"]
    assert "CORREÇÃO NECESSÁRIA" in prompt_text


def test_validate_output_no_violations():
    person = _Person(name="João", age=25)
    violations = validate_output(
        person,
        rules={"age": lambda v: v > 0, "name": lambda v: len(v) > 0},
    )
    assert violations == []


def test_validate_output_with_violation():
    person = _Person(name="João", age=-5)
    violations = validate_output(
        person,
        rules={"age": lambda v: v > 0},
    )
    assert len(violations) == 1
    assert "age" in violations[0]


def test_validate_output_multiple_violations():
    person = _Person(name="", age=-1)
    violations = validate_output(
        person,
        rules={"age": lambda v: v > 0, "name": lambda v: len(v) > 0},
    )
    assert len(violations) == 2


def test_max_retries_exceeded_message():
    errors = ["erro 1", "erro 2", "erro 3"]
    exc = MaxRetriesExceeded(errors)
    assert "3" in str(exc)
    assert exc.errors == errors
