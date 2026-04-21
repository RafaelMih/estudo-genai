# 02_rag — Retrieval-Augmented Generation

## O problema
LLMs têm conhecimento limitado ao seu treinamento (cutoff date) e não têm acesso a documentos privados. RAG resolve isso: busca documentos relevantes e os injeta no contexto antes de gerar a resposta.

## Como funciona

```
PIPELINE RAG COMPLETO:
═══════════════════════

FASE DE INGESTÃO (offline, feita uma vez):
  ┌──────────┐    ┌──────────┐    ┌───────────────┐    ┌──────────────┐
  │Documentos│───►│ Chunking │───►│  Embeddings   │───►│ Vector Store │
  │PDF/TXT/MD│    │ (04_rag) │    │ (05_embeddings│    │ (06_vector_  │
  └──────────┘    └──────────┘    └───────────────┘    │    store)    │
                                                        └──────────────┘

FASE DE QUERY (online, por pergunta):
         ┌───────────────────────────────────────────────────┐
  Query──►│ 1. Embed query                                    │
         │ 2. Busca top-k chunks no vector store             │
         │ 3. (Opcional) Re-ranking com cross-encoder        │
         │ 4. Formata chunks como contexto no prompt         │
         │ 5. LLM gera resposta baseada no contexto          │
         └───────────────────────────┬───────────────────────┘
                                     ▼
                              Resposta final

ESTRATÉGIAS DE CHUNKING:
═════════════════════════
  Fixed-size    → chunks de N tokens com overlap
                  simples, mas pode cortar frases no meio
  Sentence      → divide por sentenças (NLTK)
                  preserva unidade semântica mínima
  Recursive     → tenta dividir por §, \n, frase, palavra
                  balanceia tamanho e semântica
  Semantic      → agrupa sentenças por similaridade de embedding
                  chunks mais coerentes, mais lento

ADVANCED RAG:
══════════════
  HyDE          → gera documento hipotético, embeda ele (não a query)
  Multi-query   → gera N reformulações da query, faz N buscas, deduplica
  Re-ranking    → cross-encoder reavalia e reordena os top-k recuperados
```

## Quando RAG falha e como mitigar

| Problema | Causa | Solução |
|----------|-------|---------|
| Chunks irrelevantes recuperados | Chunking ruim ou query mal formulada | Semantic chunking + query expansion |
| Resposta ignora o contexto | Prompt fraco | Instrução explícita de usar apenas o contexto |
| Alucinação apesar do contexto | LLM "inventa" além do contexto | Instrução + eval de faithfulness |
| Contexto muito longo | Muitos chunks recuperados | Re-ranking + limitar top-k |

## Como Rodar

```bash
# Indexar documentos de exemplo
python -m scripts.ingest_docs --dir modules/rag/data/sample_docs

# Fazer uma pergunta
python -m scripts.run_rag_query --question "O que é o mecanismo de atenção?"

# Rodar pipeline diretamente
python -m modules.rag.pipeline
```

## Referências
- [RAG paper original (Lewis et al., 2020)](https://arxiv.org/abs/2005.11401)
- [Advanced RAG Techniques survey](https://arxiv.org/abs/2312.10997)
- [HyDE paper](https://arxiv.org/abs/2212.10496)
- [RAGAS evaluation framework](https://docs.ragas.io)

## Exercícios
1. Compare as 4 estratégias de chunking na mesma pergunta — qual retorna chunks mais relevantes?
2. Implemente parent-document retrieval: indexa chunks pequenos, retorna o parágrafo pai
3. Adicione um indicador de confiança: "Não sei" quando nenhum chunk tem score > threshold
4. Implemente Contextual Compression: comprime os chunks recuperados antes de enviar ao LLM
5. Use `query_expansion.py` e meça se melhora o recall no dataset de `evaluation/datasets/qa_pairs.json`


