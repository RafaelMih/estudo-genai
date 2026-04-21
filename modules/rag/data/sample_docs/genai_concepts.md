# Conceitos de IA Generativa

## Large Language Models (LLMs)

Large Language Models (LLMs) são modelos de aprendizado profundo treinados em grandes quantidades de texto. Eles aprendem a prever o próximo token em uma sequência, o que lhes dá a capacidade emergente de gerar texto coerente, responder perguntas, traduzir idiomas e realizar raciocínio complexo.

Os LLMs modernos são baseados na arquitetura Transformer, introduzida no paper "Attention Is All You Need" (Vaswani et al., 2017). Os componentes principais incluem camadas de atenção multi-head, feed-forward networks e normalização de camadas.

Exemplos proeminentes incluem GPT-4 (OpenAI), Claude (Anthropic), Gemini (Google) e Llama (Meta).

## Retrieval-Augmented Generation (RAG)

RAG é uma técnica que combina a recuperação de informações (information retrieval) com a geração de texto por LLMs. Em vez de confiar apenas no conhecimento do treinamento do modelo, o RAG busca documentos relevantes de uma base de conhecimento externa e os fornece como contexto ao LLM durante a geração.

### Pipeline do RAG

**Fase de Ingestão:**
1. Documentos são carregados de diversas fontes (PDFs, bancos de dados, websites)
2. Os documentos são divididos em chunks menores
3. Cada chunk é convertido em um embedding vetorial
4. Os embeddings são armazenados em um vector store

**Fase de Consulta:**
1. A pergunta do usuário é convertida em embedding
2. Os chunks mais similares são recuperados do vector store
3. Os chunks recuperados são injetados no prompt do LLM
4. O LLM gera uma resposta baseada no contexto fornecido

### Vantagens do RAG sobre Fine-tuning

- **Atualização de conhecimento:** Novos documentos podem ser adicionados sem retreinar o modelo
- **Rastreabilidade:** As fontes podem ser citadas na resposta
- **Custo:** Muito mais barato que fine-tuning para conhecimento factual
- **Privacidade:** Dados sensíveis permanecem na base de conhecimento e não são "memorizados" pelo modelo

## Embeddings

Embeddings são representações vetoriais de texto em espaços de alta dimensão. Textos semanticamente similares têm embeddings próximos no espaço vetorial.

Modelos populares para geração de embeddings incluem:
- **all-MiniLM-L6-v2:** Rápido, 384 dimensões, bom para uso geral
- **all-mpnet-base-v2:** Mais qualidade, 768 dimensões
- **text-embedding-3-large:** Alta qualidade via API OpenAI (1536 dimensões)

A similaridade entre embeddings é calculada principalmente via similaridade cosseno.

## Vector Stores

Vector stores são bancos de dados otimizados para busca por similaridade em alta dimensão. Eles usam algoritmos de busca aproximada como HNSW (Hierarchical Navigable Small World) para encontrar os vizinhos mais próximos eficientemente.

Exemplos populares:
- **ChromaDB:** Open-source, fácil de usar, bom para desenvolvimento
- **Pinecone:** Serviço gerenciado, escala facilmente
- **Weaviate:** Open-source com recursos avançados de filtragem
- **FAISS:** Biblioteca do Facebook, excelente performance, sem persistência nativa

## Model Context Protocol (MCP)

O Model Context Protocol (MCP) é um protocolo aberto desenvolvido pela Anthropic para padronizar como aplicações fornecem contexto e ferramentas para LLMs. Ele define:

- **Tools:** Funções que o LLM pode invocar (ex: busca web, acesso a banco de dados)
- **Resources:** Dados estáticos que o LLM pode ler (ex: arquivos, páginas web)
- **Prompts:** Templates de prompt reutilizáveis expostos pelo servidor

O MCP usa transports como stdio (processo local) e SSE (Server-Sent Events para serviços web) para comunicação entre cliente e servidor.
