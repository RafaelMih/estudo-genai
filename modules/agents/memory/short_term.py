"""Buffer de memória de curto prazo — mantém as últimas N mensagens no contexto."""

from __future__ import annotations

from shared.logger import get_logger

log = get_logger(__name__)


class ShortTermMemory:
    def __init__(self, max_messages: int = 20) -> None:
        self._messages: list[dict] = []
        self._max = max_messages

    def add(self, role: str, content: str) -> None:
        self._messages.append({"role": role, "content": content})
        if len(self._messages) > self._max:
            removed = self._messages.pop(0)
            log.debug(f"Memória cheia — removida mensagem mais antiga: {removed['role']}")

    def get_messages(self) -> list[dict]:
        return list(self._messages)

    def clear(self) -> None:
        self._messages.clear()

    @property
    def length(self) -> int:
        return len(self._messages)
