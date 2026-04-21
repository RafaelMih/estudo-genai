from collections.abc import Iterator
from typing import Any

import anthropic

MODEL = "claude-sonnet-4-6"
MAX_TOKENS_DEFAULT = 1024


class LLMClient:
    """Thin wrapper around the Anthropic SDK. Single place to swap model or add retry logic."""

    def __init__(self, api_key: str | None = None, model: str = MODEL):
        self.model = model
        self._client = anthropic.Anthropic(api_key=api_key)

    def complete(
        self,
        messages: list[dict[str, Any]],
        system: str = "",
        max_tokens: int = MAX_TOKENS_DEFAULT,
        temperature: float = 1.0,
        **kwargs: Any,
    ) -> str:
        """Send messages and return the assistant text response."""
        response = self._client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            messages=messages,
            **kwargs,
        )
        return response.content[0].text

    def complete_with_tools(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        system: str = "",
        max_tokens: int = MAX_TOKENS_DEFAULT,
    ) -> anthropic.types.Message:
        """Send messages with tool definitions and return the full Message object."""
        return self._client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system,
            tools=tools,
            messages=messages,
        )

    def stream(
        self,
        messages: list[dict[str, Any]],
        system: str = "",
        max_tokens: int = MAX_TOKENS_DEFAULT,
        temperature: float = 1.0,
    ) -> Iterator[str]:
        """Yield text tokens as they arrive via SSE streaming."""
        with self._client.messages.stream(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            messages=messages,
        ) as stream:
            yield from stream.text_stream

    def count_tokens(self, messages: list[dict[str, Any]], system: str = "") -> int:
        """Estimate token count for a message list before sending."""
        response = self._client.messages.count_tokens(
            model=self.model,
            system=system,
            messages=messages,
        )
        return response.input_tokens

    @property
    def raw(self) -> anthropic.Anthropic:
        """Access the underlying Anthropic client for advanced use cases."""
        return self._client


def build_client() -> LLMClient:
    """Convenience factory that reads API key from shared settings."""
    from shared.config import settings
    return LLMClient(api_key=settings.anthropic_api_key)
