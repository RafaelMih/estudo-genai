# Story 01 — Basic JSON Output

**Agente:** @sm (River)  
**Implementado por:** @dev (Dex)  
**Revisado por:** @qa (Quinn)  
**User Story:** US-01  
**Status:** ✅ Completa  

---

## Descrição

Como estudante, quero ver a abordagem mais simples de structured output: instruir o LLM a retornar JSON via prompt e fazer parse do resultado.

## Tasks

- [x] Criar `modules/structured_output/__init__.py` com exports públicos
- [x] Criar `modules/structured_output/basic_structured.py`
- [x] Definir função `extract_as_json(text, fields, llm)` que retorna `dict`
- [x] Prompt inclui exemplo de JSON esperado e lista de campos
- [x] Tratar `json.JSONDecodeError` com mensagem clara
- [x] Bloco `if __name__ == "__main__"` com exemplo executável

## Critérios de Aceite

- `extract_as_json("Python é uma linguagem...", ["nome", "tipo"], llm)` retorna `{"nome": "Python", "tipo": "linguagem"}`
- `json.JSONDecodeError` levanta `ValueError` com mensagem descritiva
- Executável standalone: `python -m modules.structured_output.basic_structured`

## Exemplo Input/Output

```python
text = "Python é uma linguagem de programação interpretada, de alto nível."
fields = ["nome", "tipo", "caracteristicas"]

result = extract_as_json(text, fields, llm)
# {"nome": "Python", "tipo": "linguagem de programação", "caracteristicas": ["interpretada", "alto nível"]}
```

## Arquivos Modificados

- `modules/structured_output/__init__.py` (criado)
- `modules/structured_output/basic_structured.py` (criado)
