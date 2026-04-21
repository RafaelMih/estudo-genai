# 04_agents — Agentes Autônomos

## O problema
Como fazer um LLM executar tarefas complexas de múltiplos passos, usando ferramentas externas, adaptando-se a resultados intermediários e mantendo memória do progresso?

## Como funciona

```
PADRÃO ReAct (Reasoning + Acting):
════════════════════════════════════

  Pergunta: "Qual a população do Brasil hoje?"
      │
      ▼
  ┌─────────────────────────────────────────────────────┐
  │ Thought: Preciso buscar a população atual do Brasil  │  ← LLM raciocina
  │ Action: web_search("população Brasil 2025")          │  ← LLM decide ação
  └─────────────────────────────────────────────────────┘
      │
      ▼
  [Executa web_search] → "Brasil tem ~215 milhões de habitantes"
      │
      ▼
  ┌─────────────────────────────────────────────────────┐
  │ Observation: Resultado da busca: 215 milhões         │  ← resultado da tool
  │ Thought: Tenho a informação, posso responder         │  ← LLM avalia
  │ Final Answer: A população do Brasil é ~215 milhões   │  ← resposta final
  └─────────────────────────────────────────────────────┘

TIPOS DE MEMÓRIA:
═════════════════
  Short-term  → mensagens no contexto (janela do LLM)
               desaparece quando o contexto é limpo
  Long-term   → sumarização periódica + persistência em arquivo
               permanece entre sessões

MULTI-AGENT:
═════════════
  ┌──────────────────────────────────────────────────────┐
  │  Orchestrator Agent                                   │
  │  • Recebe tarefa complexa                             │
  │  • Decompõe em subtarefas                             │
  │  • Delega a workers especializados                    │
  │  • Sintetiza resultados                               │
  └──────────────┬──────────────────────────────────────┘
                 │
    ┌────────────┼────────────┐
    ▼            ▼            ▼
  Worker A    Worker B    Worker C
 (Pesquisa)  (Análise)   (Escrita)
```

## Tools Disponíveis

| Tool | Arquivo | Descrição | Requer API key |
|------|---------|-----------|----------------|
| `web_search` | `tools/web_search.py` | DuckDuckGo search | Não |
| `calculator` | `tools/calculator.py` | Avaliador seguro de expressões | Não |
| `file_reader` | `tools/file_reader.py` | Lê arquivo local | Não |
| `python_executor` | `tools/python_executor.py` | Executa Python restrito | Não |

## Papéis Chave

| Arquivo | Classe/Função | O que ensina |
|---------|--------------|-------------|
| `simple_agent.py` | `SimpleAgent` | Tool calling single-step com Anthropic SDK |
| `react_agent.py` | `ReActAgent` | Loop ReAct implementado do zero |
| `multi_agent.py` | `Orchestrator`, `Worker` | Decomposição e delegação de tarefas |
| `memory/short_term.py` | `ShortTermMemory` | Buffer de contexto com limite de tokens |
| `memory/long_term.py` | `LongTermMemory` | Sumarização periódica + persistência |

## Como Rodar

```bash
python -m modules.agents.simple_agent
python -m modules.agents.react_agent
python scripts/run_agent.py --query "Pesquise e explique o que é RAG"
```

## Referências
- [ReAct paper (Yao et al., 2022)](https://arxiv.org/abs/2210.03629)
- [Tool use na Anthropic API](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
- [Cognitive Architectures for Language Agents](https://arxiv.org/abs/2309.02427)

## Exercícios
1. Adicione uma tool `read_rag_docs(question)` que usa o pipeline RAG do módulo 02
2. Implemente um agente com memória episódica que lembra conversas anteriores
3. Adicione um mecanismo de reflexão: após falhar uma tool, o agente tenta outra abordagem
4. Implemente Planner-Executor: um agente planeja todos os passos antes de executar
5. Adicione limite de custo: o agente para quando o número de tokens excede um threshold
