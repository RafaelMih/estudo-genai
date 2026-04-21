# GenAI Study Project

> Projeto de estudos hands-on do ecossistema completo de IA Generativa usando Anthropic Claude (`claude-sonnet-4-6`) como LLM backbone.

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
- Chave de API Anthropic ([console.anthropic.com](https://console.anthropic.com))
- ~4 GB de espaço em disco (modelos de embedding locais)

## Quick Start (5 minutos)

```bash
# 1. Clonar e entrar no projeto
cd ProjetoInicial

# 2. Configurar ambiente
cp .env.example .env
# Edite .env e adicione sua ANTHROPIC_API_KEY

# 3. Instalar dependências (instala o projeto em modo editável)
pip install -e ".[dev]"

# 4. Validar setup
python scripts/setup_env.py

# 5. Primeiro teste — chamada ao Claude
python -m modules.llm.basic_completion

# 6. Abrir notebooks interativos
jupyter lab
# → abra notebooks/00_setup_and_hello.ipynb
```

cp .env.example .env # adicione sua ANTHROPIC_API_KEY
pip install -r requirements-dev.txt
python scripts/setup_env.py # valida tudo
python scripts/ingest_docs.py --dir modules/rag/data/sample_docs
python scripts/run_rag_query.py --question "O que é RAG?"
jupyter lab # abra notebooks/00_setup_and_hello.ipynb

## Trilha de Aprendizado

```
INICIANTE ──► 01_llm ──► 07_prompt_engineering ──► 05_embeddings
                                                          │
INTERMEDIÁRIO ◄──────── vector_store ◄────────────────┘
     │
     └──► 02_rag ──► 08_eval
                         │
AVANÇADO ◄───────────────┘
   │
   └──► 03_mcp ──► 04_agents ──► construa o seu próprio módulo
```

## Estrutura do Projeto

```
ProjetoInicial/
├── shared/                  # Código compartilhado (config, LLM client, utils)
├── modules/
│   ├── llm/              # Large Language Models
│   ├── rag/              # Retrieval-Augmented Generation
│   ├── mcp/              # Model Context Protocol
│   ├── agents/           # Agentes autônomos
│   ├── embeddings/       # Embeddings e similaridade
│   ├── vector_store/     # ChromaDB e busca vetorial
│   ├── prompt_engineering/  # Engenharia de prompts
│   └── evaluation/             # Avaliação e métricas
├── notebooks/               # Jupyter notebooks interativos
├── scripts/                 # CLIs: ingest, query, agent, eval
└── tests/                   # Testes unitários com mocks
```

## Executando Scripts CLI

```bash
# Indexar documentos no ChromaDB
python scripts/ingest_docs.py --dir modules/rag/data/sample_docs

# Fazer uma pergunta com RAG
python scripts/run_rag_query.py --question "O que é o mecanismo de atenção?"

# Rodar agente ReAct
python scripts/run_agent.py --query "Pesquise e explique o que é RAG"

# Executar suite de avaliação
python scripts/run_eval.py --output modules/evaluation/reports/run_001.json
```

## Rodando os Testes

```bash
pytest tests/ -v
```

## Filosofia do Projeto

Este projeto implementa **tudo via primitivos**, sem depender de LangChain ou LlamaIndex nos módulos. O objetivo é entender o que esses frameworks fazem internamente antes de usá-los. Cada README de módulo explica o conceito, mostra a implementação primitiva e, ao final, compara com o equivalente em frameworks populares.
# estudo-genai
