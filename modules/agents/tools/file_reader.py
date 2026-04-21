"""Tool que lê arquivos locais por caminho."""

from __future__ import annotations

from pathlib import Path

TOOL_DEFINITION = {
    "name": "file_reader",
    "description": "Lê o conteúdo de um arquivo de texto local.",
    "input_schema": {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Caminho do arquivo"},
            "max_chars": {"type": "integer", "description": "Máximo de caracteres a retornar (padrão: 2000)"},
        },
        "required": ["path"],
    },
}

ALLOWED_DIRS = [
    Path("modules/rag/data"),
    Path("modules"),
]


def file_reader(path: str, max_chars: int = 2000) -> str:
    """Lê arquivo com restrição de diretórios permitidos."""
    file_path = Path(path).resolve()
    allowed = any(
        str(file_path).startswith(str(d.resolve()))
        for d in ALLOWED_DIRS
    )
    if not allowed:
        return f"Acesso negado: {path} não está em um diretório permitido."
    if not file_path.exists():
        return f"Arquivo não encontrado: {path}"
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        return content[:max_chars] + ("..." if len(content) > max_chars else "")
    except Exception as e:
        return f"Erro ao ler arquivo: {e}"
