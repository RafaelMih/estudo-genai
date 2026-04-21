# 03_mcp — Model Context Protocol

## O problema
Como padronizar a forma que aplicações fornecem ferramentas, dados e contexto para LLMs, independente de qual LLM ou framework é usado?

## Como funciona

```
ARQUITETURA MCP:
════════════════

  ┌────────────────────────────────────────────────────────┐
  │                    HOST (ex: Claude Desktop, seu app)   │
  │                                                         │
  │  ┌─────────────────┐      ┌──────────────────────────┐ │
  │  │   LLM Client    │◄────►│     MCP Client           │ │
  │  │  (Claude API)   │      │  (gerencia sessões MCP)  │ │
  │  └─────────────────┘      └──────────┬───────────────┘ │
  └──────────────────────────────────────┼─────────────────┘
                                         │ transport (stdio / SSE)
                    ┌────────────────────┼──────────────────────┐
                    │                    │   MCP SERVER          │
                    │  ┌─────────────────▼──────────────────┐   │
                    │  │           Server Core               │   │
                    │  │  • list_tools()                     │   │
                    │  │  • call_tool(name, args)            │   │
                    │  │  • list_resources()                 │   │
                    │  │  • read_resource(uri)               │   │
                    │  └────────────────────────────────────┘    │
                    └────────────────────────────────────────────┘

PRIMITIVOS DO MCP:
═══════════════════

  Tools      → funções que o LLM pode CHAMAR (side effects OK)
               ex: buscar web, executar SQL, enviar email

  Resources  → dados que o LLM pode LER (somente leitura)
               ex: conteúdo de arquivo, página web, linhas de DB

  Prompts    → templates de prompt reutilizáveis expostos pelo servidor
               ex: prompt de análise de código, prompt de resumo

TRANSPORTS:
════════════
  stdio      → servidor roda como subprocess, comunicação via stdin/stdout
               ideal para servidores locais, simples de implementar

  SSE        → servidor como serviço web, comunicação via HTTP + SSE
               ideal para servidores remotos, múltiplos clientes

PROTOCOLO:
═══════════
  JSON-RPC 2.0 sobre o transport escolhido
  Mensagens: requests (com id) e notifications (sem id)
  Lifecycle: initialize → list_tools → call_tool → ... → shutdown
```

## Papéis Chave

| Arquivo | Classe/Função | O que ensina |
|---------|--------------|-------------|
| `server/simple_server.py` | `mcp.Server` com tool | Anatomia de um servidor MCP |
| `server/file_server.py` | resources de filesystem | Primitivo Resource vs Tool |
| `server/database_server.py` | SQLite como resource | Dados estruturados via MCP |
| `client/stdio_client.py` | `ClientSession` + stdio | Conexão e discovery de tools |
| `schemas/tool_definitions.py` | Pydantic schemas | JSON Schema para tools |

## Como Rodar

```bash
# Terminal 1: iniciar servidor
python modules/mcp/server/simple_server.py

# Terminal 2: conectar cliente (abre o servidor automaticamente via subprocess)
python modules/mcp/client/stdio_client.py

# Demo de filesystem
python modules/mcp/server/file_server.py
```

No Windows dentro do Jupyter, prefira `notebook_safe_stdio_client()` em
`modules/mcp/client/stdio_client.py` para evitar `UnsupportedOperation: fileno`.

## Referências
- [MCP Specification](https://spec.modelcontextprotocol.io)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Servers Registry](https://github.com/modelcontextprotocol/servers)
- [Anthropic MCP Announcement](https://www.anthropic.com/news/model-context-protocol)

## Exercícios
1. Adicione um tool `get_weather(city)` que chama uma API pública de clima
2. Implemente um servidor MCP com recursos que expõem os documentos em `rag/data/sample_docs/`
3. Crie um servidor MCP com ferramenta de busca vetorial (wrap do ChromaDB)
4. Implemente o transport SSE para que o servidor rode como serviço web
5. Integre o servidor MCP ao agente ReAct do módulo 04 para expansão dinâmica de ferramentas
