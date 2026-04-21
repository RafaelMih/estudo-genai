"""Carrega documentos PDF, TXT e MD para texto bruto."""

from __future__ import annotations

from pathlib import Path

from shared.logger import get_logger
from shared.utils import clean_text

log = get_logger(__name__)


def _coerce_path(path: str | Path) -> Path:
    return path if isinstance(path, Path) else Path(path)


def load_txt(path: Path) -> str:
    return clean_text(path.read_text(encoding="utf-8", errors="ignore"))


def load_md(path: Path) -> str:
    return clean_text(path.read_text(encoding="utf-8", errors="ignore"))


def load_pdf(path: Path) -> str:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    pages = [page.extract_text() or "" for page in reader.pages]
    return clean_text("\n\n".join(pages))


def load_docx(path: Path) -> str:
    from docx import Document

    doc = Document(str(path))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return clean_text("\n\n".join(paragraphs))


LOADERS = {
    ".txt": load_txt,
    ".md": load_md,
    ".pdf": load_pdf,
    ".docx": load_docx,
}


def load_document(path: str | Path) -> dict:
    """Carrega um documento e retorna dict com text e metadata."""
    path = _coerce_path(path)
    suffix = path.suffix.lower()
    loader = LOADERS.get(suffix)
    if loader is None:
        raise ValueError(f"Formato não suportado: {suffix}. Suportados: {list(LOADERS)}")

    log.info(f"Carregando: {path.name}")
    text = loader(path)
    return {
        "text": text,
        "metadata": {
            "source": path.name,
            "path": str(path),
            "format": suffix,
        },
    }


def load_directory(dir_path: str | Path, recursive: bool = False) -> list[dict]:
    """Carrega todos os documentos suportados de um diretório."""
    dir_path = _coerce_path(dir_path)
    glob_fn = dir_path.rglob if recursive else dir_path.glob
    docs = []
    for suffix in LOADERS:
        for file_path in glob_fn(f"*{suffix}"):
            try:
                docs.append(load_document(file_path))
            except Exception as e:
                log.warning(f"Erro ao carregar {file_path.name}: {e}")
    log.info(f"Total carregado: {len(docs)} documentos de {dir_path}")
    return docs
