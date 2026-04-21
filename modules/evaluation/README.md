# 08_eval — Avaliação de Sistemas GenAI

## O problema
Como medir objetivamente se um sistema RAG ou agente está funcionando bem? Perplexidade não é suficiente — precisamos de métricas específicas para geração aumentada.

## Como funciona

```
HIERARQUIA DE AVALIAÇÃO:
═════════════════════════

  Nível 1: Métricas de String
  ─────────────────────────────
  BLEU, ROUGE, Exact Match
  Rápido, determinístico, mas fraco para linguagem natural

  Nível 2: Métricas Semânticas
  ─────────────────────────────
  BERTScore, Similaridade de Embedding
  Captura paráfrases, mas caro computacionalmente

  Nível 3: LLM-as-Judge
  ─────────────────────────
  Claude avalia Claude (ou outro sistema)
  Flexível e alinhado com qualidade humana, mas subjetivo

  Nível 4: Métricas RAG-específicas (RAGAS-style)
  ─────────────────────────────────────────────────
  Context Recall     → o contexto recuperado cobriu a resposta correta?
  Context Precision  → os chunks recuperados eram relevantes?
  Answer Faithfulness → a resposta se atém ao contexto ou alucina?
  Answer Relevance   → a resposta responde de fato à pergunta?

RAGAS MÉTRICAS EXPLICADAS:
════════════════════════════

  Context Recall:
    pergunta → resposta_esperada vs. chunks_recuperados
    "O contexto contém a informação para gerar a resposta correta?"
    Baixo recall = retriever está perdendo chunks importantes

  Answer Faithfulness:
    resposta_gerada vs. contexto_fornecido
    "A resposta contradiz ou inventa além do contexto?"
    Baixo faithfulness = alucinação

  Answer Relevance:
    resposta_gerada vs. pergunta_original
    "A resposta realmente responde à pergunta?"
    Baixo relevance = resposta off-topic
```

## Papéis Chave

| Arquivo | Classe/Função | O que ensina |
|---------|--------------|-------------|
| `metrics/string_metrics.py` | `rouge_score()`, `bleu_score()` | Métricas clássicas de NLP |
| `metrics/semantic_metrics.py` | `bert_score()`, `embedding_sim()` | Métricas baseadas em representação |
| `metrics/llm_judge.py` | `LLMJudge` | Avaliação com rubrica via LLM |
| `rag_eval.py` | `RAGEvaluator` | Pipeline RAGAS-style completo |
| `agent_eval.py` | `AgentEvaluator` | Taxa de acerto de tool selection |

## Como Rodar

```bash
python scripts/run_eval.py --output modules/evaluation/reports/run_001.json
python -m modules.evaluation.rag_eval
python -m modules.evaluation.metrics.llm_judge
```

## Referências
- [RAGAS paper](https://arxiv.org/abs/2309.15217)
- [G-Eval paper](https://arxiv.org/abs/2303.16634)
- [ROUGE paper](https://aclanthology.org/W04-1013/)
- [BERTScore paper](https://arxiv.org/abs/1904.09675)

## Exercícios
1. Adicione a métrica `context_precision` ao RAGEvaluator
2. Implemente comparative evaluation: compare dois sistemas RAG na mesma questão
3. Crie um dashboard HTML que visualiza os resultados de múltiplos runs
4. Implemente human evaluation annotation tool para coletar feedback humano
5. Calibre o LLM judge comparando suas notas com avaliação humana em 20 exemplos
