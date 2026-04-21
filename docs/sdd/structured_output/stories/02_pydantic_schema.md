# Story 02 — Pydantic Schema Output

**Agente:** @sm (River)  
**Implementado por:** @dev (Dex)  
**Revisado por:** @qa (Quinn)  
**User Story:** US-02  
**Status:** ✅ Completa  

---

## Descrição

Como estudante, quero usar um Pydantic `BaseModel` como contrato de saída, recebendo instâncias validadas em vez de dicts brutos.

## Tasks

- [x] Criar `modules/structured_output/pydantic_output.py`
- [x] Definir interface `OutputParser` (typing.Protocol)
- [x] Implementar `PydanticOutputParser` que recebe `type[BaseModel]`
- [x] Método `parse(text) -> BaseModel` usa `model_json_schema()` para montar prompt
- [x] Validação via `model.model_validate(data)` — levanta `pydantic.ValidationError` se inválido
- [x] Factory `build_output_parser(schema)` retorna `PydanticOutputParser`
- [x] Bloco `__main__` com exemplo de schema `TechConcept`

## Critérios de Aceite

- `parser = build_output_parser(TechConcept)` cria parser válido
- `parser.parse(text)` retorna instância `TechConcept` com campos tipados
- `pydantic.ValidationError` é propagado quando output não casa com schema
- Schema JSON é derivado automaticamente de `model_json_schema()` — sem duplicação manual

## Exemplo

```python
class TechConcept(BaseModel):
    name: str
    category: str
    year_created: int | None = None
    key_features: list[str] = []

parser = build_output_parser(TechConcept)
result = parser.parse("Transformers foi introduzido em 2017 pelo Google...")
# TechConcept(name='Transformer', category='Neural Architecture', year_created=2017, key_features=['attention', 'parallelizable'])
assert isinstance(result, TechConcept)
assert result.year_created == 2017
```

## Arquivos Modificados

- `modules/structured_output/pydantic_output.py` (criado)
