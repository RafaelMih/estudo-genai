# Story 03 — Tool-Based Extraction

**Agente:** @sm (River)  
**Implementado por:** @dev (Dex)  
**Revisado por:** @qa (Quinn)  
**User Story:** US-03  
**Status:** ✅ Completa  

---

## Descrição

Como estudante, quero usar `tool_use` (function calling) para extrair entidades estruturadas, entendendo por que essa abordagem é mais confiável do que pedir JSON no prompt.

## Por que tool_use é mais confiável?

Com tool_use, o LLM não "escreve" JSON — ele preenche parâmetros de uma função. O schema é enforced pelo próprio protocolo Claude, eliminando JSON malformado.

## Tasks

- [x] Criar `modules/structured_output/tool_based_extraction.py`
- [x] Implementar `pydantic_to_tool_schema(model_class, tool_name, description)` → `dict`
- [x] Implementar `extract_with_tool(text, schema_class, llm)` → instância do schema
- [x] Usar `llm.complete_with_tools([tool_schema], messages)` de `shared/llm_client.py`
- [x] Extrair `ToolUseBlock.input` da resposta e instanciar o model Pydantic
- [x] Levantar `ValueError` se LLM não chamou a tool esperada
- [x] Bloco `__main__` com extração de `Article` de texto jornalístico

## Critérios de Aceite

- `pydantic_to_tool_schema(Article, "extract_article", "...")` produz dict válido com `input_schema`
- `extract_with_tool(news_text, Article, llm)` retorna `Article` validado
- `ValueError` quando `stop_reason != "tool_use"`
- Compatível com `complete_with_tools` da interface existente (Anthropic + OpenAI)

## Exemplo

```python
class Article(BaseModel):
    title: str
    author: str | None = None
    date: str | None = None
    topics: list[str] = []
    summary: str

text = "O pesquisador Rafael Santos publicou ontem um estudo sobre LLMs..."
article = extract_with_tool(text, Article, llm)
# Article(title='Estudo sobre LLMs', author='Rafael Santos', date='ontem', topics=['LLM'], summary='...')
```

## Diferença vs Story 02

| | Pydantic Output Parser | Tool-Based |
|---|---|---|
| Mecanismo | JSON no prompt | function calling |
| JSON malformado | possível | impossível |
| Campos extras | parse pode falhar | LLM filtra |
| Dependência | só Pydantic | + `complete_with_tools` |

## Arquivos Modificados

- `modules/structured_output/tool_based_extraction.py` (criado)
