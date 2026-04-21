"""4 estratégias de chunking para comparação e estudo."""

from __future__ import annotations

import nltk
from shared.logger import get_logger

log = get_logger(__name__)

try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt_tab", quiet=True)


def fixed_size_chunk(text: str, size: int = 512, overlap: int = 64) -> list[str]:
    """Chunks de tamanho fixo em caracteres com overlap."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end].strip())
        start += size - overlap
    return [c for c in chunks if c]


def sentence_chunk(text: str, max_sentences: int = 5) -> list[str]:
    """Agrupa N sentenças por chunk. Preserva unidade semântica mínima."""
    sentences = nltk.sent_tokenize(text, language="portuguese")
    chunks = []
    for i in range(0, len(sentences), max_sentences):
        chunk = " ".join(sentences[i : i + max_sentences])
        if chunk.strip():
            chunks.append(chunk.strip())
    return chunks


def recursive_chunk(text: str, max_size: int = 512, overlap: int = 64) -> list[str]:
    """Divide por separadores hierárquicos: parágrafo → frase → palavra."""
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=max_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return [c.strip() for c in splitter.split_text(text) if c.strip()]


def semantic_chunk(text: str, embedder=None, threshold: float = 0.75) -> list[str]:
    """Agrupa sentenças consecutivas enquanto similaridade > threshold."""
    from modules.embeddings.local_embedder import LocalEmbedder
    from modules.embeddings.similarity import cosine_similarity

    if embedder is None:
        embedder = LocalEmbedder()

    sentences = nltk.sent_tokenize(text, language="portuguese")
    if len(sentences) <= 1:
        return sentences

    embeddings = embedder.embed_batch(sentences)

    chunks = []
    current = [sentences[0]]
    for i in range(1, len(sentences)):
        sim = cosine_similarity(embeddings[i - 1], embeddings[i])
        if sim >= threshold:
            current.append(sentences[i])
        else:
            chunks.append(" ".join(current))
            current = [sentences[i]]
    if current:
        chunks.append(" ".join(current))
    return chunks


def compare_strategies(text: str) -> None:
    """Compara todas as estratégias no mesmo texto."""
    strategies = {
        "Fixed-size (512 chars)": fixed_size_chunk(text),
        "Sentence (5 frases)": sentence_chunk(text),
        "Recursive (512 chars)": recursive_chunk(text),
    }
    for name, chunks in strategies.items():
        print(f"\n[{name}] → {len(chunks)} chunks")
        for i, c in enumerate(chunks[:2], 1):
            print(f"  [{i}] {c[:120]}...")


if __name__ == "__main__":
    sample = """
    RAG significa Retrieval-Augmented Generation. É uma técnica que combina busca de informação com geração de texto.
    O processo funciona em duas fases principais: ingestão e consulta.
    Na ingestão, documentos são carregados, divididos em chunks e convertidos em embeddings armazenados num vector store.
    Na consulta, a pergunta é convertida em embedding, os chunks mais similares são recuperados e passados ao LLM como contexto.
    Isso permite que o modelo responda com informações atualizadas e privadas sem retreinamento.
    """
    compare_strategies(sample.strip())
