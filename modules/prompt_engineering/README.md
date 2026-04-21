# 07_prompt_engineering — Engenharia de Prompts

## O problema
Como estruturar instruções para que o LLM produza respostas mais precisas, consistentes, no formato correto e com o raciocínio adequado?

## Como funciona

```
ANATOMIA DE UM PROMPT EFICAZ:
══════════════════════════════

  ┌─────────────────────────────────────────────────────────┐
  │ SYSTEM PROMPT                                            │
  │  • Papel/persona do assistente                           │
  │  • Regras e restrições                                   │
  │  • Formato de saída esperado                             │
  └──────────────────────────────────────────────────────────┘
                          +
  ┌─────────────────────────────────────────────────────────┐
  │ USER MESSAGE                                             │
  │  • Contexto (ex: documentos recuperados pelo RAG)        │
  │  • Exemplos (few-shot)                                   │
  │  • Instrução de raciocínio (CoT)                         │
  │  • Pergunta/tarefa concreta                              │
  └──────────────────────────────────────────────────────────┘
                          ↓
  ┌─────────────────────────────────────────────────────────┐
  │ ASSISTANT RESPONSE (controlada pela engenharia do prompt)│
  └──────────────────────────────────────────────────────────┘

TÉCNICAS PRINCIPAIS:
═════════════════════

  Zero-shot    → apenas instrução, sem exemplos
  Few-shot     → 2–8 exemplos (pergunta, resposta) antes da tarefa
  CoT          → "Pense passo a passo" induz raciocínio explícito
  Self-consistency → N amostras + majority vote → maior confiança
  Step-back    → reformule a pergunta em nível mais abstrato primeiro
  Structured   → força output em JSON/XML para parsing programático
```

## Técnicas e Quando Usar

| Técnica | Quando usar | Trade-off |
|---------|-------------|-----------|
| Zero-shot CoT | Raciocínio geral | Simples, mas pode errar em problemas complexos |
| Few-shot | Formato específico | Gasta tokens com exemplos |
| Self-consistency | Alta precisão necessária | N × custo de tokens |
| Step-back | Perguntas de domínio profundo | 1 chamada extra |
| Structured output | Parsing programático | Pode perder nuance |
| Meta-prompting | Melhorar qualidade do prompt | 2 chamadas (gerar + executar) |

## Papéis Chave

| Arquivo | Classe/Função | O que ensina |
|---------|--------------|-------------|
| `templates/base_template.py` | `PromptTemplate` | Separação template/dados com Jinja2 |
| `templates/few_shot.py` | `FewShotPrompt` | Seleção e formatação de exemplos |
| `templates/chain_of_thought.py` | `ZeroShotCoT`, `FewShotCoT` | Variantes de CoT |
| `templates/structured_output.py` | `JSONPrompt`, `XMLPrompt` | Output controlado |
| `techniques/self_consistency.py` | `self_consistency()` | Ensemble via sampling |
| `techniques/step_back.py` | `step_back_query()` | Abstração antes de responder |
| `techniques/meta_prompting.py` | `improve_prompt()` | LLM melhora seu próprio prompt |
| `prompt_library.py` | `PROMPTS` dict | Registro reutilizável de prompts |

## Como Rodar

```bash
python -m modules.prompt_engineering.templates.chain_of_thought
python -m modules.prompt_engineering.techniques.self_consistency
python -m modules.prompt_engineering.techniques.step_back
python -m modules.prompt_engineering.techniques.meta_prompting
```

## Referências
- [Chain-of-Thought Prompting paper](https://arxiv.org/abs/2201.11903)
- [Self-Consistency paper](https://arxiv.org/abs/2203.11171)
- [Step-Back Prompting paper](https://arxiv.org/abs/2310.06117)
- [Anthropic Prompt Engineering Guide](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering)

## Exercícios
1. Em `few_shot.py`, implemente seleção dinâmica de exemplos por similaridade semântica à query
2. Compare zero-shot vs few-shot em 5 perguntas de matemática e meça a taxa de acerto
3. Implemente Tree-of-Thought: explore múltiplos ramos de raciocínio antes de concluir
4. Crie um prompt que force o modelo a citar fontes específicas de um conjunto de documentos
5. Use `meta_prompting.py` para melhorar um prompt de RAG e compare a qualidade das respostas
