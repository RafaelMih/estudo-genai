# Architecture Doc — `modules/structured_output/`

**Agente:** @architect (Aria)  
**Status:** ✅ Aprovado  

---

## O Problema Técnico

Claude retorna `str`. Para structured output existem 3 abordagens:

```
Abordagem 1 — JSON no prompt (simples, frágil)
  prompt → "retorne JSON com campos X, Y" → parse(str)

Abordagem 2 — Pydantic + JSON no prompt (tipado, ainda frágil)
  prompt → "retorne JSON com campos X, Y" → json.loads → Model(**data)

Abordagem 3 — tool_use (confiável, schema enforced pelo LLM)
  tool_schema(pydantic_model) → complete_with_tools → ToolUseBlock.input
```

## Diagrama de Fluxo

```
texto_input
    │
    ├──► basic_structured.py
    │         │  prompt com exemplo JSON
    │         ▼
    │    llm.complete() → str → json.loads() → dict
    │
    ├──► pydantic_output.py
    │         │  prompt com schema JSON do Model
    │         ▼
    │    llm.complete() → str → json.loads() → Model(**data) → instância Pydantic
    │
    ├──► tool_based_extraction.py
    │         │  tool_schema = pydantic_to_tool_schema(Model)
    │         ▼
    │    llm.complete_with_tools(tools=[tool_schema])
    │         ▼
    │    ToolUseBlock.input → Model(**input) → instância Pydantic
    │
    └──► validation.py
              │  qualquer abordagem + retry loop
              ▼
         parse() → ValidationError? → retry(max=3) → instância validada
```

## Interface Principal

```python
# typing.Protocol — não exige herança
class OutputParser(Protocol):
    schema: type[BaseModel]

    def parse(self, text: str) -> BaseModel: ...
    def parse_tool_response(self, response: ToolResponse) -> BaseModel: ...

# Factory function (mesmo padrão de build_client)
def build_output_parser(schema: type[BaseModel]) -> OutputParser: ...
```

## Estrutura de Arquivos

```
modules/structured_output/
├── __init__.py                  # exporta OutputParser, build_output_parser
├── basic_structured.py          # US-01: JSON direto no prompt
├── pydantic_output.py           # US-02: Pydantic como contrato
├── tool_based_extraction.py     # US-03: tool_use para extração
├── validation.py                # US-04: retry com validação
└── README.md                    # docs do módulo
```

## Decisões de Design

| Decisão | Escolha | Alternativa Descartada | Motivo |
|---------|---------|----------------------|--------|
| Schema definition | Pydantic `BaseModel` | dataclasses, TypedDict | Pydantic já é dependência, tem `model_json_schema()` |
| Tool schema | Derivado de Pydantic via `model_json_schema()` | Schema manual | DRY: uma definição serve para validação e LLM |
| Retry | Loop simples com `max_retries=3` | tenacity lib | Dependência zero; suficiente para aprendizado |
| Interface | `typing.Protocol` | ABC | Consistente com o restante do projeto |

## Integração com Projeto Existente

- `build_client()` de `shared/llm_client.py` — mesmo padrão de todos os módulos
- `ToolResponse`, `ToolUseBlock` de `shared/llm_interface.py` — tipos já definidos
- `mock_llm_client` de `tests/conftest.py` — fixture de teste sem API real
