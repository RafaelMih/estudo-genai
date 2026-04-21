import json
import sys
import importlib.util
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from shared import llm_client as llm_module
from shared.llm_client import (
    ANTHROPIC_PROVIDER,
    OPENAI_PROVIDER,
    AnthropicLLMClient,
    OpenAILLMClient,
    TextBlock,
    ToolUseBlock,
    build_client,
)


class FakeAnthropicMessagesAPI:
    def __init__(self) -> None:
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if kwargs.get("tools"):
            return SimpleNamespace(
                stop_reason="tool_use",
                content=[
                    SimpleNamespace(type="tool_use", id="tool_1", name="calculator", input={"expression": "2+2"})
                ],
            )
        return SimpleNamespace(stop_reason="end_turn", content=[SimpleNamespace(type="text", text="ok anthropic")])

    def count_tokens(self, **kwargs):
        return SimpleNamespace(input_tokens=17)

    def stream(self, **kwargs):
        class _Stream:
            text_stream = ["a", "b"]

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

        return _Stream()


class FakeOpenAICompletionsAPI:
    def __init__(self) -> None:
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if kwargs.get("stream"):
            return [
                SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content="a"))]),
                SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content="b"))]),
            ]
        if kwargs.get("tools"):
            tool_call = SimpleNamespace(
                id="call_1",
                function=SimpleNamespace(name="calculator", arguments=json.dumps({"expression": "2+2"})),
            )
            message = SimpleNamespace(content="", tool_calls=[tool_call])
            return SimpleNamespace(choices=[SimpleNamespace(message=message)])
        message = SimpleNamespace(content="ok openai", tool_calls=None)
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


class FakeOpenAIClient:
    def __init__(self) -> None:
        self.chat = SimpleNamespace(completions=FakeOpenAICompletionsAPI())


@pytest.fixture(autouse=True)
def reset_settings(monkeypatch):
    monkeypatch.setattr(llm_module.settings, "anthropic_api_key", None)
    monkeypatch.setattr(llm_module.settings, "openai_api_key", None)
    monkeypatch.setattr(llm_module.settings, "llm_provider", "anthropic")
    monkeypatch.setattr(llm_module.settings, "llm_model", None)
    monkeypatch.setattr(llm_module.settings, "llm_base_url", None)


def test_build_client_resolves_anthropic(monkeypatch):
    monkeypatch.setattr(llm_module.settings, "anthropic_api_key", "sk-ant-test")
    with patch("shared.llm_client.AnthropicLLMClient") as client_cls:
        build_client()
    client_cls.assert_called_once_with(api_key="sk-ant-test", model="claude-sonnet-4-6")


def test_build_client_resolves_openai(monkeypatch):
    monkeypatch.setattr(llm_module.settings, "openai_api_key", "sk-openai-test")
    monkeypatch.setattr(llm_module.settings, "llm_provider", OPENAI_PROVIDER)
    with patch("shared.llm_client.OpenAILLMClient") as client_cls:
        build_client()
    client_cls.assert_called_once_with(api_key="sk-openai-test", model="gpt-4.1-mini", base_url=None)


def test_build_client_invalid_provider_raises():
    with pytest.raises(ValueError, match="Provider inválido"):
        build_client(provider="invalid")


def test_build_client_missing_key_raises(monkeypatch):
    monkeypatch.setattr(llm_module.settings, "llm_provider", OPENAI_PROVIDER)
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        build_client()


def test_anthropic_adapter_normalizes_tool_response():
    fake_messages = FakeAnthropicMessagesAPI()
    client = AnthropicLLMClient(api_key="sk-ant-test", client=SimpleNamespace(messages=fake_messages))

    result = client.complete_with_tools(
        messages=[{"role": "user", "content": "quanto é 2+2?"}],
        tools=[{"name": "calculator", "description": "calc", "input_schema": {"type": "object"}}],
    )

    assert result.stop_reason == "tool_use"
    assert isinstance(result.content[0], ToolUseBlock)
    assert result.content[0].name == "calculator"
    assert result.content[0].input == {"expression": "2+2"}


def test_openai_adapter_normalizes_complete_and_tools():
    fake_client = FakeOpenAIClient()
    client = OpenAILLMClient(api_key="sk-openai-test", client=fake_client)

    text = client.complete(messages=[{"role": "user", "content": "oi"}])
    tool_result = client.complete_with_tools(
        messages=[{"role": "user", "content": "quanto é 2+2?"}],
        tools=[{"name": "calculator", "description": "calc", "input_schema": {"type": "object"}}],
    )

    assert text == "ok openai"
    assert tool_result.stop_reason == "tool_use"
    assert isinstance(tool_result.content[0], ToolUseBlock)
    assert tool_result.content[0].input == {"expression": "2+2"}


def test_openai_stream_yields_tokens():
    fake_client = FakeOpenAIClient()
    client = OpenAILLMClient(api_key="sk-openai-test", client=fake_client)

    assert "".join(client.stream(messages=[{"role": "user", "content": "oi"}])) == "ab"


def test_openai_count_tokens_uses_tiktoken(monkeypatch):
    fake_tiktoken = SimpleNamespace(
        encoding_for_model=lambda model: SimpleNamespace(encode=lambda text: [1, 2, 3]),
        get_encoding=lambda name: SimpleNamespace(encode=lambda text: [1, 2, 3]),
    )
    monkeypatch.setitem(sys.modules, "tiktoken", fake_tiktoken)

    fake_client = FakeOpenAIClient()
    client = OpenAILLMClient(api_key="sk-openai-test", client=fake_client)

    assert client.count_tokens(messages=[{"role": "user", "content": "oi"}]) == 3


def test_run_agent_cli_overrides_provider_model(monkeypatch):
    run_agent = _load_script_module("run_agent_test_module", "scripts/run_agent.py")

    captured = {}

    def fake_build_client(provider=None, model=None):
        captured["provider"] = provider
        captured["model"] = model
        return "fake-client"

    class FakeAgent:
        def __init__(self, max_steps, client):
            captured["max_steps"] = max_steps
            captured["client"] = client

        def run(self, query):
            captured["query"] = query
            return "done"

    monkeypatch.setattr(run_agent, "build_client", fake_build_client)
    monkeypatch.setattr(run_agent, "ReActAgent", FakeAgent)
    monkeypatch.setattr(sys, "argv", ["run_agent", "--query", "teste", "--provider", "openai", "--model", "gpt-4.1-mini"])

    run_agent.main()

    assert captured["provider"] == "openai"
    assert captured["model"] == "gpt-4.1-mini"
    assert captured["client"] == "fake-client"
    assert captured["query"] == "teste"


def test_run_rag_query_cli_overrides_provider_model(monkeypatch):
    run_rag_query = _load_script_module("run_rag_query_test_module", "scripts/run_rag_query.py")

    captured = {}

    def fake_build_client(provider=None, model=None):
        captured["provider"] = provider
        captured["model"] = model
        return "fake-client"

    class FakePipeline:
        def __init__(self, **kwargs):
            captured["pipeline_kwargs"] = kwargs

        def query(self, question):
            captured["question"] = question
            return {"question": question, "answer": "ok", "sources": []}

    monkeypatch.setattr(run_rag_query, "build_client", fake_build_client)
    monkeypatch.setattr(run_rag_query, "RAGPipeline", FakePipeline)
    monkeypatch.setattr(
        sys,
        "argv",
        ["run_rag_query", "--question", "teste", "--provider", "openai", "--model", "gpt-4.1-mini"],
    )

    run_rag_query.main()

    assert captured["provider"] == "openai"
    assert captured["model"] == "gpt-4.1-mini"
    assert captured["pipeline_kwargs"]["llm"] == "fake-client"
    assert captured["question"] == "teste"


def _load_script_module(module_name: str, relative_path: str):
    path = Path(relative_path)
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module
