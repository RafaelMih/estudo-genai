# Story 04 — Validation & Retry Guardrails

**Agente:** @sm (River)  
**Implementado por:** @dev (Dex)  
**Revisado por:** @qa (Quinn)  
**User Story:** US-04  
**Status:** ✅ Completa  

---

## Descrição

Como estudante, quero ver retry automático quando o output do LLM não é válido, aprendendo sobre resiliência em pipelines de structured output.

## Tasks

- [x] Criar `modules/structured_output/validation.py`
- [x] Implementar `parse_with_retry(text, parser, llm, max_retries=3)` → instância Pydantic
- [x] No retry, incluir o erro de validação no prompt seguinte ("corrija este erro: ...")
- [x] Levantar `MaxRetriesExceeded` após esgotar tentativas
- [x] Implementar `validate_output(instance, rules)` para validações de negócio extras
- [x] Bloco `__main__` demonstrando retry com schema intencionalamente difícil

## Critérios de Aceite

- Primeira tentativa válida: retorna imediatamente sem retry
- Tentativa inválida: inclui erro no próximo prompt e retenta
- Após `max_retries` falhas consecutivas: levanta `MaxRetriesExceeded` com histórico de erros
- `validate_output` retorna `list[str]` de violações (vazio = válido)

## Exemplo

```python
class StrictPerson(BaseModel):
    name: str
    age: int           # deve ser positivo
    email: str         # deve conter @

result = parse_with_retry(
    text="João tem 30 anos e usa joao@email.com",
    parser=build_output_parser(StrictPerson),
    llm=llm,
    max_retries=3,
)
# StrictPerson(name='João', age=30, email='joao@email.com')

# Regras de negócio extras:
violations = validate_output(result, rules={"age": lambda v: v > 0, "email": lambda v: "@" in v})
# []  (nenhuma violação)
```

## Estratégia de Retry

```
tentativa 1: prompt original
    → ValidationError? → adiciona ao prompt: "Erro anterior: {error}. Corrija e retorne JSON válido."
tentativa 2: prompt + erro 1
    → ValidationError? → adiciona ao prompt: "Erro anterior: {error}. Corrija e retorne JSON válido."
tentativa 3: prompt + erro 2
    → ValidationError? → levanta MaxRetriesExceeded([erros])
```

## Arquivos Modificados

- `modules/structured_output/validation.py` (criado)
