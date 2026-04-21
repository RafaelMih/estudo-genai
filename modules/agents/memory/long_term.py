"""Memória de longo prazo via sumarização periódica + persistência em JSON."""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime

from shared.llm_client import LLMClient, build_client
from shared.logger import get_logger

log = get_logger(__name__)

SUMMARIZE_SYSTEM = "Você é um assistente que cria resumos concisos de conversas. Preserve fatos importantes, decisões e contexto relevante."


class LongTermMemory:
    def __init__(self, persist_path: str = "agent_memory.json", summarize_every: int = 10) -> None:
        self._path = Path(persist_path)
        self._summarize_every = summarize_every
        self._client: LLMClient | None = None
        self._summaries: list[dict] = self._load()

    def _load(self) -> list[dict]:
        if self._path.exists():
            return json.loads(self._path.read_text())
        return []

    def _save(self) -> None:
        self._path.write_text(json.dumps(self._summaries, ensure_ascii=False, indent=2))

    def summarize_and_store(self, messages: list[dict]) -> str:
        if self._client is None:
            self._client = build_client()
        conversation = "\n".join(f"{m['role'].upper()}: {m['content'][:200]}" for m in messages)
        prompt = f"Resuma esta conversa preservando fatos importantes:\n\n{conversation}"
        summary = self._client.complete([{"role": "user", "content": prompt}], system=SUMMARIZE_SYSTEM, max_tokens=300)
        entry = {"timestamp": datetime.now().isoformat(), "summary": summary}
        self._summaries.append(entry)
        self._save()
        log.info(f"Memória de longo prazo: {len(self._summaries)} resumos salvos")
        return summary

    def get_context(self, max_summaries: int = 3) -> str:
        if not self._summaries:
            return ""
        recent = self._summaries[-max_summaries:]
        return "MEMÓRIA DE LONGO PRAZO:\n" + "\n---\n".join(s["summary"] for s in recent)

    def clear(self) -> None:
        self._summaries = []
        if self._path.exists():
            self._path.unlink()
