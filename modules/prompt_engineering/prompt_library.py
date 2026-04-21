"""Registro central de prompts reutilizáveis do projeto."""

from modules.prompt_engineering.templates.base_template import PromptTemplate

PROMPTS: dict[str, PromptTemplate] = {
    "rag_answer": PromptTemplate(
        """Use os documentos abaixo para responder à pergunta. Se a informação não estiver presente, diga explicitamente.

DOCUMENTOS:
{% for i, doc in docs %}
[{{ i }}] {{ doc }}
{% endfor %}

PERGUNTA: {{ question }}

RESPOSTA:"""
    ),
    "summarize": PromptTemplate(
        """Resuma o texto a seguir em {{ sentences }} frases objetivas. Foque em: {{ focus }}.

TEXTO:
{{ text }}

RESUMO:"""
    ),
    "classify": PromptTemplate(
        """Classifique o texto em uma das categorias: {{ categories | join(', ') }}.
Responda apenas com o nome da categoria, sem explicações.

TEXTO: {{ text }}

CATEGORIA:"""
    ),
    "extract_entities": PromptTemplate(
        """Extraia do texto as seguintes entidades em formato JSON:
{{ entity_types | join(', ') }}

TEXTO:
{{ text }}

JSON:"""
    ),
    "code_review": PromptTemplate(
        """Revise o seguinte código {{ language }} e identifique:
1. Bugs ou erros lógicos
2. Problemas de performance
3. Melhorias de legibilidade

CÓDIGO:
```{{ language }}
{{ code }}
```

REVISÃO:"""
    ),
}


def get_prompt(name: str) -> PromptTemplate:
    if name not in PROMPTS:
        raise KeyError(f"Prompt '{name}' não encontrado. Disponíveis: {list(PROMPTS)}")
    return PROMPTS[name]


if __name__ == "__main__":
    print("Prompts disponíveis na biblioteca:")
    for name in PROMPTS:
        print(f"  - {name}")
