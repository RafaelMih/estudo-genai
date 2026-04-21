# 05_embeddings — Embeddings e Similaridade Semântica

## O problema
Como representar o significado de um texto de forma que o computador possa comparar e buscar por similaridade semântica, não apenas por palavras-chave exatas?

## Como funciona

```
ESPAÇO DE EMBEDDINGS:
═════════════════════

  "gato"    ──► [0.12, -0.45, 0.78, ..., 0.31]  (384 dimensões)
  "felino"  ──► [0.11, -0.43, 0.76, ..., 0.29]  ← muito próximo!
  "avião"   ──► [-0.82, 0.91, -0.14, ..., 0.55] ← distante

  Similaridade cosseno:
    sim("gato", "felino") ≈ 0.95  ← semanticamente similares
    sim("gato", "avião")  ≈ 0.12  ← semanticamente distantes

PIPELINE DE EMBEDDING LOCAL (sentence-transformers):
══════════════════════════════════════════════════════

  texto
    │
    ▼
  Tokenização (WordPiece/BPE)
    │
    ▼
  BERT/MPNet encoder  ──► token embeddings [seq_len × hidden_dim]
    │
    ▼
  Mean Pooling  ──► vetor único [hidden_dim]
    │
    ▼
  L2 Normalization  ──► vetor de norma 1.0 (pronto para cosseno)
    │
    ▼
  Embedding final: [384] float32
```

## Modelos Disponíveis

| Modelo | Dimensão | Velocidade | Qualidade | Uso |
|--------|----------|-----------|-----------|-----|
| `all-MiniLM-L6-v2` | 384 | Rápido | Boa | Desenvolvimento, default do projeto |
| `all-mpnet-base-v2` | 768 | Médio | Muito boa | Produção |
| `paraphrase-multilingual-MiniLM-L12-v2` | 384 | Médio | Boa (multilíngue) | Textos em português |
| Via API (Voyage AI) | 1024+ | API call | Excelente | Produção de alta qualidade |

## Papéis Chave

| Arquivo | Classe/Função | O que ensina |
|---------|--------------|-------------|
| `embedder.py` | Protocol `Embedder` | Interfaces estruturais em Python |
| `local_embedder.py` | `LocalEmbedder` | Inferência local com sentence-transformers |
| `api_embedder.py` | `APIEmbedder` | Troca de implementação sem mudar callers |
| `similarity.py` | `cosine_similarity`, etc. | Métricas de distância vetorial |
| `visualizer.py` | `plot_embeddings()` | t-SNE para visualizar clusters semânticos |
| `benchmark.py` | `run_benchmark()` | Comparação de modelos |

## Como Rodar

```bash
python -m modules.embeddings.local_embedder
python -m modules.embeddings.similarity
python -m modules.embeddings.visualizer      # gera embedding_clusters.png
python -m modules.embeddings.benchmark
```

## Referências
- [Sentence-BERT paper](https://arxiv.org/abs/1908.10084)
- [MTEB Benchmark (ranking de modelos)](https://huggingface.co/spaces/mteb/leaderboard)
- [Visualizing embeddings with t-SNE](https://distill.pub/2016/misread-tsne/)

## Exercícios
1. Modifique `visualizer.py` para colorir por categoria (ex: frases sobre IA vs. frases sobre culinária)
2. Em `benchmark.py`, adicione o modelo multilíngue e teste com frases em português
3. Implemente `semantic_search(query, corpus)` em `similarity.py` que retorna top-5 resultados
4. Explore o efeito de comprimento do texto no vetor de embedding: frase curta vs. parágrafo longo
5. Calcule a similaridade entre todas as perguntas de `modules/evaluation/datasets/qa_pairs.json`
