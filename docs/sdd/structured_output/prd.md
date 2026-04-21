# PRD — Módulo `structured_output`

**Agente:** @pm (Morgan)  
**Status:** ✅ Aprovado  
**Versão:** 1.0  

---

## Problema

LLMs retornam texto livre. Em aplicações reais precisamos de dados estruturados: um JSON com campos específicos, um objeto tipado, uma lista de entidades. Sem um contrato claro, o output do LLM é frágil — qualquer variação de phrasing quebra o sistema downstream.

## Objetivo

Implementar um módulo que demonstre **3 estratégias de structured output** com Claude, do mais simples ao mais robusto, usando Pydantic como contrato de dados.

## Usuários-Alvo

Estudantes do projeto GenAI que já completaram os módulos `llm` e `prompt_engineering` e querem entender como garantir outputs confiáveis de LLMs.

## User Stories

| ID | Como... | Quero... | Para... |
|----|---------|---------|---------|
| US-01 | estudante | ver JSON gerado diretamente pelo LLM | entender a abordagem mais simples |
| US-02 | estudante | usar um Pydantic model como schema | ter validação automática de tipos |
| US-03 | estudante | usar tool_use para extração de entidades | entender a abordagem mais confiável |
| US-04 | estudante | ver retry automático quando output é inválido | aprender sobre validação + resiliência |

## Critérios de Aceite do Módulo

- [ ] `basic_structured.py` produz um dict Python válido a partir de texto livre
- [ ] `pydantic_output.py` retorna instâncias Pydantic validadas sem erros de tipo
- [ ] `tool_based_extraction.py` usa `complete_with_tools` para extrair entidades nomeadas
- [ ] `validation.py` faz retry automático (máx. 3 tentativas) se JSON é inválido
- [ ] Todos os módulos usam `build_client()` de `shared/llm_client.py`
- [ ] Testes unitários passam sem chamadas reais à API (usando `mock_llm_client`)

## Out of Scope (v1)

- Streaming de structured output
- Structured output via OpenAI Structured Outputs API
- Async/parallel extraction
- Fine-tuning para schema adherence

## Dependências

- `pydantic>=2.7.0` — já no `pyproject.toml`
- `shared/llm_client.py` — `build_client()`, `complete_with_tools()`
- `shared/llm_interface.py` — `ToolResponse`, `ToolUseBlock`
