"""Story 01 — Abordagem mais simples: JSON via prompt, sem schema formal."""

from __future__ import annotations

import json
from typing import Any

from shared.llm_client import build_client
from shared.llm_interface import LLM

_SYSTEM = (
    "Você é um extrator de informações. "
    "Retorne APENAS um objeto JSON válido, sem markdown, sem explicações."
)


def extract_as_json(text: str, fields: list[str], llm: LLM) -> dict[str, Any]:
    """Extrai campos de `text` e retorna como dict.

    Abordagem simples: o prompt instrui o LLM a retornar JSON com os campos
    solicitados. Frágil para textos ambíguos, mas didática para entender o
    ponto de partida antes de usar schemas formais.
    """
    fields_list = ", ".join(f'"{f}"' for f in fields)
    prompt = (
        f"Extraia as seguintes informações do texto e retorne um JSON com exatamente esses campos: {fields_list}\n\n"
        f"Texto:\n{text}\n\n"
        f'Exemplo de formato esperado: {{"{fields[0]}": "valor", ...}}'
    )
    raw = llm.complete(
        messages=[{"role": "user", "content": prompt}],
        system=_SYSTEM,
        temperature=0.0,
    )
    cleaned = _strip_markdown_fences(raw)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"LLM retornou JSON inválido. Output bruto:\n{raw}\nErro: {exc}"
        ) from exc


def _strip_markdown_fences(text: str) -> str:
    """Remove ```json ... ``` se o LLM incluiu fences mesmo sendo instruído a não."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    return text.strip()


if __name__ == "__main__":
    from rich.console import Console
    from rich.pretty import pprint

    console = Console()
    llm = build_client()

    console.rule("[bold]Story 01 — Basic JSON Output[/bold]")
    console.print("\n[dim]Extraindo campos de um texto sobre Python...[/dim]\n")

    sample = (
        "Python é uma linguagem de programação interpretada, de alto nível e propósito geral. "
        "Foi criada por Guido van Rossum e lançada em 1991. "
        "É conhecida por sua sintaxe simples e legibilidade."
    )
    result = extract_as_json(
        text=sample,
        fields=["nome", "criador", "ano_lancamento", "caracteristicas"],
        llm=llm,
    )
    pprint(result)
    console.print("\n[green]✓ JSON extraído com sucesso![/green]")
