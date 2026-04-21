"""Define a interface Protocol para embedders — qualquer implementação que satisfaça
os métodos abaixo é um Embedder válido, sem herança explícita."""

from typing import Protocol, runtime_checkable


@runtime_checkable
class Embedder(Protocol):
    def embed_one(self, text: str) -> list[float]:
        """Retorna embedding de um único texto."""
        ...

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Retorna embeddings de uma lista de textos."""
        ...

    @property
    def dimension(self) -> int:
        """Dimensão do vetor de embedding."""
        ...
