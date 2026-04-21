"""Embedding via API compatível com OpenAI (ex: Voyage AI).
Demonstra como trocar a implementação de Embedder sem mudar os callers."""

from __future__ import annotations

import httpx

from shared.logger import get_logger

log = get_logger(__name__)


class APIEmbedder:
    """Chama uma API de embedding compatível com OpenAI (/v1/embeddings)."""

    def __init__(self, api_key: str, base_url: str = "https://api.voyageai.com/v1", model: str = "voyage-3") -> None:
        self._model = model
        self._headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        self._base_url = base_url
        self._dim: int | None = None

    def embed_one(self, text: str) -> list[float]:
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        response = httpx.post(
            f"{self._base_url}/embeddings",
            headers=self._headers,
            json={"model": self._model, "input": texts},
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()["data"]
        embeddings = [item["embedding"] for item in sorted(data, key=lambda x: x["index"])]
        if self._dim is None and embeddings:
            self._dim = len(embeddings[0])
        return embeddings

    @property
    def dimension(self) -> int:
        if self._dim is None:
            self.embed_one("warmup")
        return self._dim or 1024
