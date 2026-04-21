import time
from contextlib import contextmanager
from collections.abc import Generator
import re


def clean_text(text: str) -> str:
    """Remove excessive whitespace and normalize line breaks."""
    text = re.sub(r"\r\n", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def truncate(text: str, max_chars: int = 200, suffix: str = "...") -> str:
    """Truncate text for display purposes."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars - len(suffix)] + suffix


def chunk_list(lst: list, size: int) -> list[list]:
    """Split a list into chunks of given size."""
    return [lst[i : i + size] for i in range(0, len(lst), size)]


@contextmanager
def timer(label: str = "operation") -> Generator[None, None, None]:
    """Context manager that prints elapsed time."""
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        print(f"[timer] {label}: {elapsed:.3f}s")


def format_sources(chunks: list[dict]) -> str:
    """Format retrieved chunks as a numbered source list for prompts."""
    lines = []
    for i, chunk in enumerate(chunks, 1):
        source = chunk.get("metadata", {}).get("source", "unknown")
        text = chunk.get("text", "")
        lines.append(f"[{i}] (source: {source})\n{text}")
    return "\n\n".join(lines)
