# GenAI Study Project

> Projeto de estudos hands-on do ecossistema completo de IA Generativa com provider LLM configurável: Anthropic/Claude ou OpenAI/Codex.

## O que você vai aprender

| Módulo                | Conceito central                                          | Aplicação real                     |
| --------------------- | --------------------------------------------------------- | ---------------------------------- |
| 01_llm                | Chamadas de API, streaming, visão, parâmetros de sampling | Chatbots, assistentes              |
| 02_rag                | Chunking, embeddings, retrieval, re-ranking, HyDE         | Busca em documentos internos       |
| 03_mcp                | Model Context Protocol, tools, resources, transports      | Integração de ferramentas externas |
| 04_agents             | ReAct loop, tool use, memória, multi-agent                | Automação de tarefas complexas     |
| 05_embeddings         | Espaço vetorial, similaridade cosseno, clustering         | Busca semântica, recomendação      |
| vector_store          | HNSW, ANN search, filtros de metadados (ChromaDB)         | Banco de dados de conhecimento     |
| 07_prompt_engineering | Few-shot, CoT, structured output, self-consistency        | Controle de qualidade de respostas |
| 08_eval               | RAGAS, LLM-as-judge, BLEU/ROUGE, BERTScore                | Medição objetiva de qualidade      |

## Pré-requisitos

- Python 3.10+
- Chave de API do provider desejado:
  - Anthropic: https://console.anthropic.com
  - OpenAI: https://platform.openai.com
- ~4 GB de espaço em disco (modelos de embedding locais)

## Quick Start (5 minutos)

```bash
# 1. Clonar e entrar no projeto
cd ProjetoInicial

# 2. Configurar ambiente
cp .env.example .env
# Edite .env e configure LLM_PROVIDER + chave correspondente

# 3. Instalar dependências (instala o projeto em modo editável)
pip install -e ".[dev]"

# 4. Validar setup
python -m scripts.setup_env

# 5. Primeiro teste
python -m modules.llm.basic_completion

# 6. Abrir notebooks interativos
jupyter lab
# → abra notebooks/00_setup_and_hello.ipynb
```

Exemplos de configuração:

```bash
# Anthropic / Claude
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
LLM_MODEL=claude-sonnet-4-6

# OpenAI / Codex-compatible
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4.1-mini
```

## Estrutura do Projeto

```text
ProjetoInicial/
├── shared/                  # Código compartilhado (config, LLM client, utils)
├── modules/
│   ├── llm/                 # Large Language Models
│   ├── rag/                 # Retrieval-Augmented Generation
│   ├── mcp/                 # Model Context Protocol
│   ├── agents/              # Agentes autônomos
│   ├── embeddings/          # Embeddings e similaridade
│   ├── vector_store/        # ChromaDB e busca vetorial
│   ├── prompt_engineering/  # Engenharia de prompts
│   └── evaluation/          # Avaliação e métricas
├── notebooks/               # Jupyter notebooks interativos
├── scripts/                 # CLIs: ingest, query, agent, eval
└── tests/                   # Testes unitários com mocks
```

## Executando Scripts CLI

```bash
# Indexar documentos no ChromaDB
python -m scripts.ingest_docs --dir modules/rag/data/sample_docs

# Fazer uma pergunta com RAG
python -m scripts.run_rag_query --question "O que é o mecanismo de atenção?"

# Provider/modelo podem ser sobrescritos por CLI
python -m scripts.run_rag_query --provider openai --model gpt-4.1-mini --question "O que é RAG?"

# Rodar agente ReAct
python -m scripts.run_agent --query "Pesquise e explique o que é RAG"

# Executar suite de avaliação
python -m scripts.run_eval --output modules/evaluation/reports/run_001.json
```

## Rodando os Testes

```bash
pytest tests/ -v
```

## Filosofia do Projeto

Este projeto implementa **tudo via primitivos**, sem depender de LangChain ou LlamaIndex nos módulos. O objetivo é entender o que esses frameworks fazem internamente antes de usá-los. Cada README de módulo explica o conceito, mostra a implementação primitiva e, quando fizer sentido, destaca diferenças entre providers.
