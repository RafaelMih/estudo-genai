"""Story 04 — Retry automático e validações de negócio para structured output."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pydantic
from pydantic import BaseModel

from modules.structured_output.pydantic_output import OutputParser, build_output_parser
from shared.llm_client import build_client
from shared.llm_interface import LLM


class MaxRetriesExceeded(Exception):
    """Levantado quando todos os retries de parse falharam."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__(f"Falhou após {len(errors)} tentativa(s). Último erro: {errors[-1]}")


def parse_with_retry(
    text: str,
    schema: type[BaseModel],
    llm: LLM | None = None,
    max_retries: int = 3,
) -> BaseModel:
    """Tenta fazer parse de `text` para `schema`, retentando com feedback de erro.

    A cada falha, o erro de validação é incluído no próximo prompt — o LLM
    aprende com o próprio erro e corrige na próxima tentativa.
    """
    resolved_llm = llm or build_client()
    parser = build_output_parser(schema, resolved_llm)

    current_text = text
    errors: list[str] = []

    for attempt in range(1, max_retries + 1):
        try:
            return parser.parse(current_text)
        except (ValueError, pydantic.ValidationError) as exc:
            error_msg = str(exc)
            errors.append(error_msg)
            if attempt == max_retries:
                break
            # acrescenta o erro ao contexto para a próxima tentativa
            current_text = (
                f"{text}\n\n"
                f"[CORREÇÃO NECESSÁRIA — tentativa {attempt}/{max_retries}]\n"
                f"O output anterior falhou com o seguinte erro:\n{error_msg}\n"
                f"Corrija e retorne um JSON válido que satisfaça o schema."
            )

    raise MaxRetriesExceeded(errors)


def validate_output(
    instance: BaseModel,
    rules: dict[str, Callable[[Any], bool]],
) -> list[str]:
    """Aplica regras de negócio a uma instância Pydantic já validada.

    Retorna lista de violações (vazia = sem problemas).
    Separa validação de schema (Pydantic) de validação de negócio (esta função).
    """
    violations: list[str] = []
    for field, rule in rules.items():
        value = getattr(instance, field, None)
        if not rule(value):
            violations.append(f"Campo '{field}' violou a regra de negócio (valor: {value!r})")
    return violations


if __name__ == "__main__":
    from rich.console import Console

    class StrictPerson(BaseModel):
        name: str
        age: int
        email: str

    console = Console()
    llm = build_client()

    console.rule("[bold]Story 04 — Validation & Retry[/bold]")
    console.print("\n[dim]Extraindo StrictPerson com retry automático...[/dim]\n")

    text = "João tem 30 anos e usa joao@email.com"
    result = parse_with_retry(text, StrictPerson, llm, max_retries=3)

    console.print(result.model_dump_json(indent=2))

    violations = validate_output(
        result,
        rules={
            "age": lambda v: isinstance(v, int) and v > 0,
            "email": lambda v: isinstance(v, str) and "@" in v,
        },
    )
    if violations:
        console.print(f"\n[red]Violações de negócio:[/red] {violations}")
    else:
        console.print("\n[green]✓ Sem violações de negócio![/green]")
