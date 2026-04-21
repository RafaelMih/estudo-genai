"""Story 02 — Pydantic como contrato de saída: schema derivado do model, validação automática."""

from __future__ import annotations

import json
from typing import Any, Protocol, runtime_checkable

import pydantic
from pydantic import BaseModel

from shared.llm_client import build_client
from shared.llm_interface import LLM, ToolResponse, ToolUseBlock

_SYSTEM = (
    "Você é um extrator de informações estruturadas. "
    "Retorne APENAS um objeto JSON válido que satisfaça o schema fornecido. "
    "Sem markdown, sem explicações."
)


@runtime_checkable
class OutputParser(Protocol):
    """Contrato para parsers de saída estruturada."""

    schema: type[BaseModel]

    def parse(self, text: str) -> BaseModel: ...

    def parse_tool_response(self, response: ToolResponse) -> BaseModel: ...


class PydanticOutputParser:
    """Instancia e valida um Pydantic BaseModel a partir do output do LLM."""

    def __init__(self, schema: type[BaseModel], llm: LLM) -> None:
        self.schema = schema
        self._llm = llm
        self._json_schema = json.dumps(schema.model_json_schema(), ensure_ascii=False, indent=2)

    def parse(self, text: str) -> BaseModel:
        """Pede ao LLM para extrair de `text` e valida contra o schema Pydantic."""
        prompt = (
            f"Extraia informações do texto abaixo e retorne um JSON que satisfaça este schema:\n\n"
            f"```json\n{self._json_schema}\n```\n\n"
            f"Texto:\n{text}"
        )
        raw = self._llm.complete(
            messages=[{"role": "user", "content": prompt}],
            system=_SYSTEM,
            temperature=0.0,
        )
        cleaned = _strip_fences(raw)
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise ValueError(f"JSON inválido do LLM:\n{raw}\nErro: {exc}") from exc
        return self.schema.model_validate(data)

    def parse_tool_response(self, response: ToolResponse) -> BaseModel:
        """Extrai o resultado de uma resposta tool_use e valida contra o schema."""
        for block in response.content:
            if isinstance(block, ToolUseBlock):
                return self.schema.model_validate(block.input)
        raise ValueError("Nenhum ToolUseBlock encontrado na resposta.")


def build_output_parser(schema: type[BaseModel], llm: LLM | None = None) -> PydanticOutputParser:
    """Factory — mesmo padrão de build_client() no projeto."""
    resolved_llm = llm or build_client()
    return PydanticOutputParser(schema=schema, llm=resolved_llm)


def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    return text.strip()


if __name__ == "__main__":
    from rich.console import Console

    class TechConcept(BaseModel):
        name: str
        category: str
        year_created: int | None = None
        key_features: list[str] = []

    console = Console()
    llm = build_client()

    console.rule("[bold]Story 02 — Pydantic Output Parser[/bold]")
    console.print("\n[dim]Extraindo TechConcept de texto sobre Transformers...[/dim]\n")

    text = (
        "O mecanismo de Transformer foi introduzido em 2017 no paper 'Attention Is All You Need' "
        "pelo Google Brain. É uma arquitetura de rede neural baseada em self-attention, "
        "paralelizável e que revolucionou o processamento de linguagem natural."
    )
    parser = build_output_parser(TechConcept, llm)
    result = parser.parse(text)

    console.print(result.model_dump_json(indent=2))
    console.print(f"\n[green]✓ Instância Pydantic criada: {type(result).__name__}[/green]")
    assert isinstance(result, TechConcept)
