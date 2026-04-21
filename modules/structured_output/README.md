# Módulo: Structured Output

## O Problema

LLMs retornam texto livre. Em pipelines de produção precisamos de dados estruturados — um JSON com campos específicos, um objeto tipado, uma lista de entidades. Sem contrato, o output do LLM é frágil: qualquer variação de phrasing quebra o sistema downstream.

## Como Funciona

Três estratégias em ordem crescente de confiabilidade:

```
Estratégia 1 — JSON no prompt (basic_structured.py)
══════════════════════════════════════════════════
  texto ──► prompt("retorne JSON com campos X,Y") ──► llm.complete()
               ──► json.loads(output) ──► dict

  + Simples de entender
  - JSON malformado possível, campos extras, campo errado

Estratégia 2 — Pydantic schema (pydantic_output.py)
════════════════════════════════════════════════════
  texto ──► prompt(json_schema) ──► llm.complete()
               ──► json.loads ──► Model.model_validate() ──► instância tipada

  + Validação automática de tipos
  - Ainda depende de o LLM gerar JSON válido

Estratégia 3 — tool_use (tool_based_extraction.py)
═══════════════════════════════════════════════════
  texto ──► complete_with_tools(tool_schema) ──► ToolUseBlock.input
               ──► Model.model_validate(input) ──► instância tipada

  + JSON malformado impossível (protocolo garante)
  + Campos extras filtrados pelo LLM automaticamente
  - Requer suporte a tool_use no provider

Resiliência — retry automático (validation.py)
══════════════════════════════════════════════
  parse() falhou? → adiciona erro ao prompt → retenta (máx. 3x)
  validate_output() → regras de negócio extras além do schema
```

## Papéis Chave

| Classe/Função | Arquivo | Papel |
|---|---|---|
| `OutputParser` | `pydantic_output.py` | Protocol — contrato do parser |
| `PydanticOutputParser` | `pydantic_output.py` | Implementação com schema Pydantic |
| `build_output_parser()` | `pydantic_output.py` | Factory (padrão do projeto) |
| `pydantic_to_tool_schema()` | `tool_based_extraction.py` | Converte BaseModel → tool schema |
| `extract_with_tool()` | `tool_based_extraction.py` | Extração via tool_use |
| `parse_with_retry()` | `validation.py` | Retry com feedback de erro |
| `validate_output()` | `validation.py` | Regras de negócio extras |

## SDD — Artefatos de Spec

Este módulo foi criado via **Spec-Driven Development** com AIOX:
- [PRD](../../docs/sdd/structured_output/prd.md)
- [Architecture Doc](../../docs/sdd/structured_output/architecture.md)
- [Stories](../../docs/sdd/structured_output/stories/)

## Como Rodar

```bash
# Story 01 — JSON simples
python -m modules.structured_output.basic_structured

# Story 02 — Pydantic schema
python -m modules.structured_output.pydantic_output

# Story 03 — tool_use
python -m modules.structured_output.tool_based_extraction

# Story 04 — retry + validação
python -m modules.structured_output.validation
```

## Exercícios

1. Adicione streaming de JSON parcial usando `llm.stream()` e `json.JSONDecoder`
2. Compare o número de tokens usados em cada estratégia com `llm.count_tokens()`
3. Implemente extração batch: receba uma lista de textos e processe em paralelo
4. Adicione suporte a schemas aninhados (BaseModel com campo do tipo outro BaseModel)
