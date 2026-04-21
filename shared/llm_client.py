from __future__ import annotations

import json
from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import Any

from shared.config import settings
from shared.llm_interface import LLM, TextBlock, ToolResponse, ToolUseBlock

ANTHROPIC_PROVIDER = "anthropic"
OPENAI_PROVIDER = "openai"
DEFAULT_ANTHROPIC_MODEL = "claude-sonnet-4-6"
DEFAULT_OPENAI_MODEL = "gpt-4.1-mini"
MAX_TOKENS_DEFAULT = 1024


class LLMClient(LLM, ABC):
    provider: str
    model: str

    @abstractmethod
    def complete(
        self,
        messages: list[dict[str, Any]],
        system: str = "",
        max_tokens: int = MAX_TOKENS_DEFAULT,
        temperature: float = 1.0,
        **kwargs: Any,
    ) -> str: ...

    @abstractmethod
    def complete_with_tools(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        system: str = "",
        max_tokens: int = MAX_TOKENS_DEFAULT,
    ) -> ToolResponse: ...

    @abstractmethod
    def stream(
        self,
        messages: list[dict[str, Any]],
        system: str = "",
        max_tokens: int = MAX_TOKENS_DEFAULT,
        temperature: float = 1.0,
    ) -> Iterator[str]: ...

    @abstractmethod
    def count_tokens(self, messages: list[dict[str, Any]], system: str = "") -> int: ...

    @property
    @abstractmethod
    def raw(self) -> Any: ...


class AnthropicLLMClient(LLMClient):
    def __init__(self, api_key: str, model: str = DEFAULT_ANTHROPIC_MODEL, client: Any | None = None):
        self.provider = ANTHROPIC_PROVIDER
        self.model = model
        if client is not None:
            self._client = client
            return

        import anthropic

        self._client = anthropic.Anthropic(api_key=api_key)

    def complete(
        self,
        messages: list[dict[str, Any]],
        system: str = "",
        max_tokens: int = MAX_TOKENS_DEFAULT,
        temperature: float = 1.0,
        **kwargs: Any,
    ) -> str:
        response = self._client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            messages=_to_anthropic_messages(messages),
            **kwargs,
        )
        return "".join(block.text for block in response.content if getattr(block, "type", "") == "text").strip()

    def complete_with_tools(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        system: str = "",
        max_tokens: int = MAX_TOKENS_DEFAULT,
    ) -> ToolResponse:
        response = self._client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system,
            tools=tools,
            messages=_to_anthropic_messages(messages),
        )
        content: list[TextBlock | ToolUseBlock] = []
        for block in response.content:
            if block.type == "text":
                content.append(TextBlock(type="text", text=block.text))
            elif block.type == "tool_use":
                content.append(ToolUseBlock(type="tool_use", id=block.id, name=block.name, input=block.input))
        stop_reason = "tool_use" if response.stop_reason == "tool_use" else "end_turn"
        return ToolResponse(stop_reason=stop_reason, content=content)

    def stream(
        self,
        messages: list[dict[str, Any]],
        system: str = "",
        max_tokens: int = MAX_TOKENS_DEFAULT,
        temperature: float = 1.0,
    ) -> Iterator[str]:
        with self._client.messages.stream(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            messages=_to_anthropic_messages(messages),
        ) as stream:
            yield from stream.text_stream

    def count_tokens(self, messages: list[dict[str, Any]], system: str = "") -> int:
        response = self._client.messages.count_tokens(
            model=self.model,
            system=system,
            messages=_to_anthropic_messages(messages),
        )
        return response.input_tokens

    @property
    def raw(self) -> Any:
        return self._client


class OpenAILLMClient(LLMClient):
    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_OPENAI_MODEL,
        base_url: str | None = None,
        client: Any | None = None,
    ) -> None:
        self.provider = OPENAI_PROVIDER
        self.model = model
        if client is not None:
            self._client = client
            return

        from openai import OpenAI

        kwargs: dict[str, Any] = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        self._client = OpenAI(**kwargs)

    def complete(
        self,
        messages: list[dict[str, Any]],
        system: str = "",
        max_tokens: int = MAX_TOKENS_DEFAULT,
        temperature: float = 1.0,
        **kwargs: Any,
    ) -> str:
        response = self._client.chat.completions.create(
            model=self.model,
            messages=_to_openai_messages(messages, system=system),
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs,
        )
        return response.choices[0].message.content or ""

    def complete_with_tools(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        system: str = "",
        max_tokens: int = MAX_TOKENS_DEFAULT,
    ) -> ToolResponse:
        response = self._client.chat.completions.create(
            model=self.model,
            messages=_to_openai_messages(messages, system=system),
            tools=_to_openai_tools(tools),
            tool_choice="auto",
            max_tokens=max_tokens,
        )
        message = response.choices[0].message
        content: list[TextBlock | ToolUseBlock] = []
        if message.content:
            content.append(TextBlock(type="text", text=message.content))
        for tool_call in message.tool_calls or []:
            args = tool_call.function.arguments or "{}"
            parsed_args = json.loads(args)
            content.append(
                ToolUseBlock(
                    type="tool_use",
                    id=tool_call.id,
                    name=tool_call.function.name,
                    input=parsed_args,
                )
            )
        stop_reason = "tool_use" if message.tool_calls else "end_turn"
        return ToolResponse(stop_reason=stop_reason, content=content)

    def stream(
        self,
        messages: list[dict[str, Any]],
        system: str = "",
        max_tokens: int = MAX_TOKENS_DEFAULT,
        temperature: float = 1.0,
    ) -> Iterator[str]:
        stream = self._client.chat.completions.create(
            model=self.model,
            messages=_to_openai_messages(messages, system=system),
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            if delta:
                yield delta

    def count_tokens(self, messages: list[dict[str, Any]], system: str = "") -> int:
        try:
            import tiktoken
        except ImportError as exc:
            raise NotImplementedError(
                "count_tokens para OpenAI requer `tiktoken` instalado para estimativa local."
            ) from exc

        try:
            encoding = tiktoken.encoding_for_model(self.model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")

        serialized = json.dumps({"system": system, "messages": _to_openai_messages(messages)}, ensure_ascii=False)
        return len(encoding.encode(serialized))

    @property
    def raw(self) -> Any:
        return self._client


def build_client(
    provider: str | None = None,
    model: str | None = None,
    base_url: str | None = None,
) -> LLMClient:
    resolved_provider = (provider or settings.llm_provider or ANTHROPIC_PROVIDER).strip().lower()
    resolved_base_url = base_url or settings.llm_base_url

    if resolved_provider == ANTHROPIC_PROVIDER:
        api_key = settings.anthropic_api_key
        if not api_key:
            raise ValueError("Provider 'anthropic' selecionado, mas ANTHROPIC_API_KEY não está configurada.")
        resolved_model = _resolve_model(resolved_provider, provider, model)
        return AnthropicLLMClient(api_key=api_key, model=resolved_model)

    if resolved_provider == OPENAI_PROVIDER:
        api_key = settings.openai_api_key
        if not api_key:
            raise ValueError("Provider 'openai' selecionado, mas OPENAI_API_KEY não está configurada.")
        resolved_model = _resolve_model(resolved_provider, provider, model)
        return OpenAILLMClient(api_key=api_key, model=resolved_model, base_url=resolved_base_url)

    raise ValueError(
        f"Provider inválido: {resolved_provider}. Use um destes: {ANTHROPIC_PROVIDER}, {OPENAI_PROVIDER}."
    )


def _to_anthropic_messages(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    converted: list[dict[str, Any]] = []
    for message in messages:
        content = message["content"]
        if isinstance(content, str):
            converted.append({"role": message["role"], "content": content})
            continue

        if isinstance(content, list):
            converted.append(
                {
                    "role": message["role"],
                    "content": [_to_anthropic_content_block(item) for item in content],
                }
            )
            continue

        raise TypeError(f"Formato de conteúdo não suportado para Anthropic: {type(content)!r}")
    return converted


def _to_anthropic_content_block(item: Any) -> dict[str, Any]:
    if isinstance(item, TextBlock):
        return {"type": "text", "text": item.text}
    if isinstance(item, ToolUseBlock):
        return {"type": "tool_use", "id": item.id, "name": item.name, "input": item.input}
    if isinstance(item, dict):
        return item
    raise TypeError(f"Bloco Anthropic não suportado: {type(item)!r}")


def _to_openai_messages(messages: list[dict[str, Any]], system: str = "") -> list[dict[str, Any]]:
    converted: list[dict[str, Any]] = []
    if system:
        converted.append({"role": "system", "content": system})

    for message in messages:
        role = message["role"]
        content = message["content"]

        if role == "assistant" and isinstance(content, list):
            text_parts: list[str] = []
            tool_calls: list[dict[str, Any]] = []
            for item in content:
                if isinstance(item, TextBlock):
                    text_parts.append(item.text)
                elif isinstance(item, ToolUseBlock):
                    tool_calls.append(
                        {
                            "id": item.id,
                            "type": "function",
                            "function": {
                                "name": item.name,
                                "arguments": json.dumps(item.input, ensure_ascii=False),
                            },
                        }
                    )
                elif isinstance(item, dict) and item.get("type") == "text":
                    text_parts.append(item["text"])
                elif isinstance(item, dict) and item.get("type") == "tool_use":
                    tool_calls.append(
                        {
                            "id": item["id"],
                            "type": "function",
                            "function": {
                                "name": item["name"],
                                "arguments": json.dumps(item["input"], ensure_ascii=False),
                            },
                        }
                    )
            payload: dict[str, Any] = {"role": "assistant", "content": "\n".join(text_parts) if text_parts else ""}
            if tool_calls:
                payload["tool_calls"] = tool_calls
            converted.append(payload)
            continue

        if role == "user" and isinstance(content, list) and content and _is_tool_result_list(content):
            for item in content:
                converted.append(
                    {
                        "role": "tool",
                        "tool_call_id": item["tool_use_id"],
                        "content": str(item["content"]),
                    }
                )
            continue

        if isinstance(content, str):
            converted.append({"role": role, "content": content})
            continue

        if isinstance(content, list):
            converted.append({"role": role, "content": _to_openai_content(content)})
            continue

        raise TypeError(f"Formato de conteúdo não suportado para OpenAI: {type(content)!r}")

    return converted


def _to_openai_content(content: list[Any]) -> list[dict[str, Any]]:
    converted: list[dict[str, Any]] = []
    for item in content:
        if isinstance(item, TextBlock):
            converted.append({"type": "text", "text": item.text})
            continue
        if isinstance(item, dict) and item.get("type") == "text":
            converted.append({"type": "text", "text": item["text"]})
            continue
        if isinstance(item, dict) and item.get("type") == "image":
            source = item.get("source", {})
            if source.get("type") != "base64":
                raise NotImplementedError("OpenAI adapter suporta apenas imagens em base64 no formato atual.")
            url = f"data:{source['media_type']};base64,{source['data']}"
            converted.append({"type": "image_url", "image_url": {"url": url}})
            continue
        raise NotImplementedError(f"Bloco multimodal não suportado para OpenAI: {item!r}")
    return converted


def _to_openai_tools(tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
    converted: list[dict[str, Any]] = []
    for tool in tools:
        converted.append(
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": tool.get("input_schema", {"type": "object", "properties": {}}),
                },
            }
        )
    return converted


def _is_tool_result_list(content: list[Any]) -> bool:
    return all(isinstance(item, dict) and item.get("type") == "tool_result" for item in content)


def _resolve_model(resolved_provider: str, explicit_provider: str | None, explicit_model: str | None) -> str:
    if explicit_model:
        return explicit_model

    if explicit_provider and explicit_provider.strip().lower() != (settings.llm_provider or "").strip().lower():
        return _default_model_for_provider(resolved_provider)

    configured_model = settings.llm_model
    if configured_model:
        return configured_model
    return _default_model_for_provider(resolved_provider)


def _default_model_for_provider(provider: str) -> str:
    if provider == OPENAI_PROVIDER:
        return DEFAULT_OPENAI_MODEL
    return DEFAULT_ANTHROPIC_MODEL
