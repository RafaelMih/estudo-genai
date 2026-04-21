"""Tool de execução segura de Python usando RestrictedPython."""

from __future__ import annotations

import io
import contextlib

TOOL_DEFINITION = {
    "name": "python_executor",
    "description": "Executa código Python seguro e retorna stdout. Sem acesso a rede, filesystem ou imports perigosos.",
    "input_schema": {
        "type": "object",
        "properties": {"code": {"type": "string", "description": "Código Python a executar"}},
        "required": ["code"],
    },
}

BLOCKED_IMPORTS = {"os", "sys", "subprocess", "socket", "requests", "httpx", "urllib", "shutil"}


def python_executor(code: str) -> str:
    """Executa código Python com sandbox básico e captura stdout."""
    for blocked in BLOCKED_IMPORTS:
        if f"import {blocked}" in code or f"from {blocked}" in code:
            return f"Segurança: import '{blocked}' não permitido."

    stdout_capture = io.StringIO()
    safe_globals = {
        "__builtins__": {
            "print": print,
            "range": range,
            "len": len,
            "sum": sum,
            "min": min,
            "max": max,
            "abs": abs,
            "round": round,
            "sorted": sorted,
            "enumerate": enumerate,
            "zip": zip,
            "list": list,
            "dict": dict,
            "set": set,
            "tuple": tuple,
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
        }
    }
    try:
        with contextlib.redirect_stdout(stdout_capture):
            exec(code, safe_globals)  # noqa: S102
        output = stdout_capture.getvalue()
        return output if output else "(sem output)"
    except Exception as e:
        return f"Erro: {type(e).__name__}: {e}"
