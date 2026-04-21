from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable


@dataclass(slots=True)
class TextBlock:
    type: str
    text: str


@dataclass(slots=True)
class ToolUseBlock:
    type: str
    id: str
    name: str
    input: dict[str, Any]


@dataclass(slots=True)
class ToolResponse:
    stop_reason: str
    content: list[TextBlock | ToolUseBlock]


@runtime_checkable
class LLM(Protocol):
    provider: str
    model: str

    def complete(
        self,
        messages: list[dict[str, Any]],
        system: str = "",
        max_tokens: int = 1024,
        temperature: float = 1.0,
        **kwargs: Any,
    ) -> str: ...

    def complete_with_tools(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        system: str = "",
        max_tokens: int = 1024,
    ) -> ToolResponse: ...

    def stream(
        self,
        messages: list[dict[str, Any]],
        system: str = "",
        max_tokens: int = 1024,
        temperature: float = 1.0,
    ) -> Iterator[str]: ...

    def count_tokens(self, messages: list[dict[str, Any]], system: str = "") -> int: ...
