# CLAUDE.md — GenAI Study Project

## Propósito

Projeto de estudos hands-on do ecossistema completo de IA Generativa, usando Anthropic Claude (`claude-sonnet-4-6`) como backbone de LLM. Cada módulo é independente, executável e auto-documentado.

## Arquitetura Geral

```
FLUXO DE DADOS PRINCIPAL:
══════════════════════════════════════════════════════════════════

  texto bruto ──► [05_embeddings] ──► vetores ──► [vector_store] ──► ChromaDB
                                                          │
  query do usuário ──► [05_embeddings] ──► vetor ────────┘
                                                  top-k chunks
                                                       │
  chunks + query ──────────────────────────────► [02_rag] ──► [01_llm] ──► resposta
                                                                  ▲
  tools + contexto ──► [03_mcp] ──► tool calls ──► [04_agents] ──┘
                                                       │
  prompts ──► [07_prompt_engineering] ──────────────── ┘
                                                       │
  saídas ──────────────────────────────────────► [08_eval] ──► métricas

ORDEM DE APRENDIZADO RECOMENDADA:
  01_llm → 05_embeddings → vector_store → 02_rag → 03_mcp → 04_agents → 07_prompt_engineering → 08_eval
```

## Layout do Repositório

| Diretório                     | Propósito                                                              |
| ----------------------------- | ---------------------------------------------------------------------- |
| `shared/`                     | Config, LLM client, logger e utils compartilhados por todos os módulos |
| `modules/llm/`                | Integração com LLM: completions, streaming, visão, parâmetros          |
| `modules/rag/`                | RAG completo: chunking, retrieval, re-ranking, HyDE                    |
| `modules/mcp/`                | Model Context Protocol: servidor e cliente stdio/SSE                   |
| `modules/agents/`             | Agentes autônomos: ReAct, multi-agent, tool use, memória               |
| `modules/embeddings/`         | Embeddings locais e via API, similaridade, visualização                |
| `modules/vector_store/`       | ChromaDB: CRUD, filtros de metadados, persistência                     |
| `modules/prompt_engineering/` | Técnicas: few-shot, CoT, ToT, structured output                        |
| `modules/evaluation/`         | Avaliação: RAGAS, LLM-as-judge, BLEU/ROUGE, BERTScore                  |
| `notebooks/`                  | Notebooks Jupyter interativos para cada módulo                         |
| `scripts/`                    | CLIs: ingest, query, agent runner, eval runner                         |
| `tests/`                      | Testes unitários com mocks (sem chamadas reais à API)                  |

## Configuração do Ambiente

```bash
# 1. Copiar template de variáveis de ambiente
cp .env.example .env
# Editar .env e adicionar sua ANTHROPIC_API_KEY

# 2. Instalar dependências (instala shared/ e modules/ como pacote editável)
pip install -e ".[dev]"

# 3. Validar setup
python scripts/setup_env.py

# 4. (Opcional) Abrir notebooks interativos
jupyter lab
```

## Variáveis de Ambiente

| Variável             | Obrigatória | Padrão                             | Descrição                      |
| -------------------- | ----------- | ---------------------------------- | ------------------------------ |
| `ANTHROPIC_API_KEY`  | sim         | —                                  | Chave da API Claude            |
| `CHROMA_PERSIST_DIR` | não         | `./modules/vector_store/chroma_db` | Diretório de dados do ChromaDB |
| `EMBEDDING_MODEL`    | não         | `all-MiniLM-L6-v2`                 | Modelo sentence-transformers   |
| `LOG_LEVEL`          | não         | `INFO`                             | Verbosidade do log             |
| `TAVILY_API_KEY`     | não         | —                                  | Busca web rica nos agentes     |

## Executando os Módulos

| Módulo        | Comando                                                            | O que faz                      |
| ------------- | ------------------------------------------------------------------ | ------------------------------ |
| 01_llm        | `python -m modules.llm.basic_completion`                           | Primeira chamada ao Claude     |
| 01_llm        | `python -m modules.llm.streaming_completion`                       | Stream de tokens em tempo real |
| 02_rag        | `python scripts/ingest_docs.py --dir modules/rag/data/sample_docs` | Indexa documentos              |
| 02_rag        | `python scripts/run_rag_query.py --question "O que é atenção?"`    | Pergunta com RAG               |
| 03_mcp        | `python modules/mcp/server/simple_server.py`                       | Inicia servidor MCP            |
| 03_mcp        | `python modules/mcp/client/stdio_client.py`                        | Conecta e chama tools          |
| 04_agents     | `python scripts/run_agent.py --query "Pesquise transformers"`      | Agente ReAct                   |
| 05_embeddings | `python -m modules.embeddings.local_embedder`                      | Embeddings locais              |
| 05_embeddings | `python -m modules.embeddings.visualizer`                          | Plot t-SNE de clusters         |
| 08_eval       | `python scripts/run_eval.py --output reports/run_001.json`         | Suite de avaliação             |

## Executando os Testes

```bash
pytest tests/ -v                        # todos os testes
pytest tests/test_rag/ -v               # apenas RAG
pytest tests/ -v --tb=short            # saída compacta
```

## Decisões Chave de Design

- **Sem LangChain/LlamaIndex nos módulos** — implementação via primitivos para forçar entendimento do que os frameworks fazem internamente. Os READMEs mostram o equivalente LangChain após a versão primitiva.
- **Model em um único lugar** — `shared/llm_client.py` define `MODEL = "claude-sonnet-4-6"`. Trocar o modelo = editar uma linha.
- **Protocol-based interfaces** — `Embedder` e `VectorStore` são `typing.Protocol`. Trocar implementação não exige herança explícita.
- **MCP como processo separado** — servidor roda como subprocess, nunca importado diretamente. Reflete deploy real.
- **Testes com mocks** — `conftest.py` fornece `mock_llm_client` via `pytest-mock`. Rápidos e gratuitos.
- **ChromaDB gitignored** — dados do vector store são efêmeros. `scripts/ingest_docs.py` sempre reconstrói.

## Estrutura dos READMEs de Módulo

Cada `modules/0N_nome/README.md` cobre:

1. **O problema** — qual desafio essa tecnologia resolve?
2. **Como funciona** — explicação conceitual com diagrama ASCII
3. **Papéis chave** — arquitetura do módulo, classes principais
4. **Referências** — papers e links relevantes
5. **Como rodar** — comando exato para executar standalone
6. **Exercícios** — extensões sugeridas para aprofundar
