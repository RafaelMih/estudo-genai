# 01_llm — Large Language Models

## O problema
Como interagir programaticamente com um modelo de linguagem grande, controlando formato, tamanho, estilo e capacidades de saída?

## Como funciona

Este módulo agora usa uma camada LLM multi-provider do projeto. A API interna continua a mesma:

```python
from shared.llm_client import build_client

client = build_client()  # resolve provider/model via .env
response = client.complete(
    messages=[{"role": "user", "content": "Olá!"}],
    system="Você é um assistente útil.",
    max_tokens=1024,
    temperature=1.0,
)
```

Providers suportados no projeto:

- `anthropic` com modelos Claude
- `openai` com modelos OpenAI/Codex configuráveis

## Conceitos Chave

### Tokens
- Unidade básica de texto processada pelo modelo (~0.75 palavras em inglês, ~0.5 em português)
- Janela de contexto: quantidade máxima de tokens que o modelo processa de uma vez
- O tamanho da janela depende do provider/modelo configurado

### Parâmetros de Sampling
| Parâmetro | Efeito | Quando usar |
|-----------|--------|-------------|
| `temperature` (0–2) | Criatividade vs. determinismo | Baixo para fatos, alto para criação |
| `top_p` (0–1) | Filtra o vocabulário por probabilidade acumulada | Alternativa ao temperature |
| `max_tokens` | Limite de tokens na resposta | Controle de custo e tamanho |

### Streaming
- A API interna do projeto normaliza streaming textual entre providers
- Reduz latência percebida para o usuário
- Usado em chatbots para exibir respostas em tempo real

### Multimodal
- O projeto aceita imagens em base64 no formato interno comum
- Cada adapter traduz isso para o formato esperado pelo provider

## Papéis Chave

| Arquivo | Classe/Função | O que ensina |
|---------|--------------|-------------|
| `basic_completion.py` | função `main()` | Anatomia mínima de uma chamada |
| `streaming_completion.py` | função `stream_response()` | SSE e UX incremental |
| `conversation_history.py` | classe `Conversation` | Gerência de estado stateless |
| `parameters.py` | função `compare_temperatures()` | Efeito dos parâmetros de sampling |
| `vision.py` | função `describe_image()` | Entrada multimodal |

## Como Rodar

```bash
python -m modules.llm.basic_completion
python -m modules.llm.streaming_completion
python -m modules.llm.conversation_history
python -m modules.llm.parameters
python -m modules.llm.vision --image path/to/image.png

# Sobrescrita de provider/modelo em exemplos com CLI
python -m modules.llm.vision --provider openai --model gpt-4.1-mini --image path/to/image.png
```

## Referências
- [Anthropic API Docs](https://docs.anthropic.com)
- [OpenAI API Docs](https://platform.openai.com/docs)
- [Attention Is All You Need (paper original Transformer)](https://arxiv.org/abs/1706.03762)

## Exercícios
1. Compare a mesma chamada em dois providers diferentes usando `.env` ou flags de CLI.
2. Em `conversation_history.py`, implemente um comando `/clear` para resetar o histórico.
3. Em `vision.py`, envie múltiplas imagens na mesma mensagem e peça uma comparação.
4. Calcule o custo estimado de uma conversa usando `count_tokens()` em `shared/llm_client.py`.
5. Adicione um terceiro provider seguindo o mesmo padrão de adapter.
