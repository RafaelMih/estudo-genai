from __future__ import annotations

from collections.abc import Iterator
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class LLM(Protocol):
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
    ) -> Any: ...

    def stream(
        self,
        messages: list[dict[str, Any]],
        system: str = "",
        max_tokens: int = 1024,
        temperature: float = 1.0,
    ) -> Iterator[str]: ...

    def count_tokens(self, messages: list[dict[str, Any]], system: str = "") -> int: ...
