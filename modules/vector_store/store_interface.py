"""Protocol abstrato para vector stores — troque ChromaDB por FAISS sem mudar callers."""

from typing import Protocol, runtime_checkable


@runtime_checkable
class VectorStore(Protocol):
    def add(
        self,
        texts: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict],
        ids: list[str],
    ) -> None: ...

    def query(
        self,
        query_embedding: list[float],
        n_results: int = 5,
        where: dict | None = None,
    ) -> list[dict]: ...

    def delete(self, ids: list[str]) -> None: ...

    def count(self) -> int: ...
