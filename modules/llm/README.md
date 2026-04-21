# 01_llm — Large Language Models

## O problema
Como interagir programaticamente com um modelo de linguagem grande, controlando formato, tamanho, estilo e capacidades de saída?

## Como funciona

```
ARQUITETURA DE UMA CHAMADA LLM:
════════════════════════════════

  Desenvolvedor
      │
      │  messages = [{"role": "user", "content": "Olá!"}]
      │  system   = "Você é um assistente útil."
      │
      ▼
  ┌─────────────────────────────────────────┐
  │          Anthropic SDK                   │
  │  client.messages.create(                │
  │    model="claude-sonnet-4-6",           │
  │    max_tokens=1024,                     │
  │    temperature=1.0,                     │
  │    system=system,                       │
  │    messages=messages,                   │
  │  )                                      │
  └──────────────────┬──────────────────────┘
                     │  HTTPS / SSE
                     ▼
  ┌──────────────────────────────────────────┐
  │          Anthropic API                    │
  │                                          │
  │  Tokenização → Transformer forward pass  │
  │  → Sampling (temperature, top_p, top_k)  │
  │  → Detokenização                          │
  └──────────────────┬───────────────────────┘
                     │
                     ▼
  response.content[0].text  →  "Olá! Como posso ajudar?"

CONVERSA MULTI-TURN:
  messages acumula alternando "user" e "assistant"
  A API é STATELESS — o cliente gerencia o histórico completo
```

## Conceitos Chave

### Tokens
- Unidade básica de texto processada pelo modelo (~0.75 palavras em inglês, ~0.5 em português)
- Janela de contexto: quantidade máxima de tokens que o modelo processa de uma vez
- `claude-sonnet-4-6` tem janela de 200K tokens

### Parâmetros de Sampling
| Parâmetro | Efeito | Quando usar |
|-----------|--------|-------------|
| `temperature` (0–2) | Criatividade vs. determinismo | Baixo para fatos, alto para criação |
| `top_p` (0–1) | Filtra o vocabulário por probabilidade acumulada | Alternativa ao temperature |
| `max_tokens` | Limite de tokens na resposta | Controle de custo e tamanho |

### Streaming
- A API retorna tokens via SSE (Server-Sent Events) conforme são gerados
- Reduz latência percebida para o usuário
- Usado em chatbots para exibir respostas em tempo real

### Multimodal
- Claude aceita imagens junto com texto em `content` blocks
- Formato: `{"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": "..."}}`

## Papéis Chave

| Arquivo | Classe/Função | O que ensina |
|---------|--------------|-------------|
| `basic_completion.py` | função `main()` | Anatomia mínima de uma chamada |
| `streaming_completion.py` | função `stream_response()` | SSE e UX incremental |
| `conversation_history.py` | classe `Conversation` | Gerência de estado stateless |
| `parameters.py` | função `compare_temperatures()` | Efeito dos parâmetros de sampling |
| `vision.py` | função `describe_image()` | Content blocks multimodal |

## Como Rodar

```bash
python -m modules.llm.basic_completion
python -m modules.llm.streaming_completion
python -m modules.llm.conversation_history    # REPL interativo
python -m modules.llm.parameters
python -m modules.llm.vision --image path/to/image.png
```

## Referências
- [Anthropic API Docs](https://docs.anthropic.com)
- [Attention Is All You Need (paper original Transformer)](https://arxiv.org/abs/1706.03762)
- [Claude Models Overview](https://docs.anthropic.com/en/docs/about-claude/models)

## Exercícios
1. Modifique `parameters.py` para comparar `top_p` em vez de `temperature`
2. Em `conversation_history.py`, implemente um comando `/clear` para resetar o histórico
3. Em `vision.py`, envie múltiplas imagens na mesma mensagem e peça uma comparação
4. Calcule o custo estimado de uma conversa usando `count_tokens()` em `shared/llm_client.py`
5. Implemente cache de prompt usando o parâmetro `cache_control` do SDK Anthropic
