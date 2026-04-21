"""Story 03 — tool_use para extração estruturada: schema enforced pelo protocolo Claude."""

from __future__ import annotations

from pydantic import BaseModel

from shared.llm_client import build_client
from shared.llm_interface import LLM, ToolUseBlock


def pydantic_to_tool_schema(
    model_class: type[BaseModel],
    tool_name: str,
    description: str,
) -> dict:
    """Converte um Pydantic BaseModel em schema de tool compatível com complete_with_tools.

    O schema JSON é derivado automaticamente — nenhuma definição duplicada.
    """
    json_schema = model_class.model_json_schema()
    # remove $defs recursivos que podem confundir alguns providers
    json_schema.pop("$defs", None)
    json_schema.pop("title", None)
    return {
        "name": tool_name,
        "description": description,
        "input_schema": json_schema,
    }


def extract_with_tool(
    text: str,
    schema_class: type[BaseModel],
    llm: LLM | None = None,
    tool_name: str = "extract_structured",
    tool_description: str = "Extrai informações estruturadas do texto.",
) -> BaseModel:
    """Usa tool_use para extrair e validar dados do `text`.

    Mais confiável do que JSON no prompt: o LLM preenche parâmetros de função,
    eliminando JSON malformado e campos extras não previstos no schema.
    """
    resolved_llm = llm or build_client()
    tool_schema = pydantic_to_tool_schema(schema_class, tool_name, tool_description)

    response = resolved_llm.complete_with_tools(
        messages=[{"role": "user", "content": f"Extraia as informações do texto:\n\n{text}"}],
        tools=[tool_schema],
        system="Você é um extrator de informações. Use a tool fornecida para retornar os dados estruturados.",
    )

    for block in response.content:
        if isinstance(block, ToolUseBlock) and block.name == tool_name:
            return schema_class.model_validate(block.input)

    raise ValueError(
        f"LLM não chamou a tool '{tool_name}'. stop_reason={response.stop_reason!r}. "
        "Verifique se o provider suporta tool_use e se o schema é válido."
    )


if __name__ == "__main__":
    from rich.console import Console

    class Article(BaseModel):
        title: str
        author: str | None = None
        date: str | None = None
        topics: list[str] = []
        summary: str

    console = Console()
    llm = build_client()

    console.rule("[bold]Story 03 — Tool-Based Extraction[/bold]")
    console.print("\n[dim]Extraindo Article de texto jornalístico via tool_use...[/dim]\n")

    news = (
        "A pesquisadora Ana Lima publicou ontem, 20 de abril de 2025, um estudo pioneiro "
        "sobre o uso de LLMs em diagnósticos médicos. O trabalho, apresentado no congresso "
        "MedAI 2025, demonstra que modelos de linguagem podem auxiliar na triagem de pacientes "
        "com precisão superior a 90% para certas condições. Os tópicos abordados incluem "
        "ética em IA, privacidade de dados e integração com sistemas de saúde existentes."
    )

    schema = pydantic_to_tool_schema(Article, "extract_article", "Extrai metadados de um artigo.")
    console.print("[dim]Tool schema gerado:[/dim]")
    import json
    console.print(json.dumps(schema, indent=2, ensure_ascii=False))

    article = extract_with_tool(news, Article, llm, "extract_article", "Extrai metadados de um artigo.")
    console.print("\n[bold]Resultado:[/bold]")
    console.print(article.model_dump_json(indent=2))
    console.print(f"\n[green]✓ Extração via tool_use: {type(article).__name__}[/green]")
