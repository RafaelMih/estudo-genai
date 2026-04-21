# vector_store — Banco de Dados Vetorial com ChromaDB

## O problema

Como armazenar e buscar eficientemente milhões de vetores de alta dimensão por similaridade, em tempo sublinear?

## Como funciona

```
BUSCA ANN (Approximate Nearest Neighbor):
══════════════════════════════════════════

  Busca Exata (brute-force):
    Para cada query → compare com TODOS os N vetores → O(N×D)
    N=1M vetores, D=384 → 384M operações por query → lento!

  HNSW (Hierarchical Navigable Small World):
    Grafo hierárquico em múltiplas camadas:
    Camada 2 (esparsa)  ──── poucos nós, conexões longas
    Camada 1            ──── mais nós
    Camada 0 (densa)    ──── todos os nós, conexões curtas

    Busca: entra pelo topo → desce para a camada mais densa
           seguindo os vizinhos mais próximos → sub-logarítmico!

  ChromaDB usa HNSW internamente via hnswlib.

ARQUITETURA DO CHROMADB:
═════════════════════════

  ┌─────────────────────────────────────────────────────┐
  │                  ChromaDB Client                     │
  │  PersistentClient(path="./chroma_db")               │
  └──────────────────────────┬──────────────────────────┘
                             │
                    ┌────────┴────────┐
                    │   Collections    │
                    │  (como tabelas)  │
                    └────────┬────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                   │
    ┌─────┴──────┐   ┌───────┴──────┐   ┌──────┴──────┐
    │ HNSW Index │   │  Metadados   │   │  Documentos │
    │  (vetores) │   │ (filtráveis) │   │  (textos)   │
    └────────────┘   └──────────────┘   └─────────────┘

  Busca com filtro (hybrid):
    1. Filtra por metadados (SQL-like) → reduz espaço de busca
    2. Busca ANN nos vetores restantes → retorna top-k
```

## Papéis Chave

| Arquivo                 | Classe/Função          | O que ensina                            |
| ----------------------- | ---------------------- | --------------------------------------- |
| `store_interface.py`    | Protocol `VectorStore` | Interface abstrata para trocar backends |
| `chroma_store.py`       | `ChromaVectorStore`    | CRUD completo no ChromaDB               |
| `metadata_filtering.py` | exemplos de `where`    | Filtros estruturados + busca vetorial   |
| `persistence.py`        | `demo_persistence()`   | Persistência em disco e recarga         |

## Como Rodar

```bash
python -m modules.vector_store.chroma_store
python -m modules.vector_store.metadata_filtering
python -m modules.vector_store.persistence
```

## Referências

- [ChromaDB Docs](https://docs.trychroma.com)
- [HNSW paper](https://arxiv.org/abs/1603.09320)
- [Approximate Nearest Neighbors Oh Yeah (ANNOY)](https://github.com/spotify/annoy)
- [ANN Benchmarks](https://ann-benchmarks.com)

## Exercícios

1. Implemente um `FaissStore` que satisfaça o Protocol `VectorStore`
2. Meça o tempo de busca conforme aumenta o número de documentos (10, 100, 1000, 10000)
3. Implemente busca por metadados com `$in` operator (ex: filtrar por múltiplas fontes)
4. Implemente um mecanismo de atualização de documentos (delete + re-insert)
5. Compare a qualidade dos resultados com e sem filtro de metadados no mesmo corpus
