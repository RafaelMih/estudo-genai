"""Template de prompt baseado em Jinja2 — separa estrutura do template dos dados."""

from __future__ import annotations

from jinja2 import Environment, StrictUndefined, Template


class PromptTemplate:
    """Template reutilizável que aceita variáveis Jinja2."""

    def __init__(self, template_str: str) -> None:
        self._env = Environment(undefined=StrictUndefined, keep_trailing_newline=True)
        self._template: Template = self._env.from_string(template_str)
        self._defaults: dict = {}

    def partial(self, **kwargs) -> "PromptTemplate":
        """Retorna novo template com algumas variáveis pré-preenchidas."""
        new_tmpl = PromptTemplate(self._template.source)
        new_tmpl._defaults = {**self._defaults, **kwargs}
        return new_tmpl

    def render(self, **kwargs) -> str:
        merged = {**self._defaults, **kwargs}
        return self._template.render(**merged)

    def __call__(self, **kwargs) -> str:
        return self.render(**kwargs)


RAG_TEMPLATE = PromptTemplate(
    """Use os seguintes documentos para responder à pergunta. \
Se a resposta não estiver nos documentos, diga "Não encontrei essa informação nos documentos fornecidos."

DOCUMENTOS:
{% for i, doc in docs %}
[{{ i }}] {{ doc }}
{% endfor %}

PERGUNTA: {{ question }}

RESPOSTA:"""
)

SUMMARIZE_TEMPLATE = PromptTemplate(
    """Resuma o seguinte texto em {{ max_sentences }} frases, focando em {{ focus }}:

TEXTO:
{{ text }}

RESUMO:"""
)


if __name__ == "__main__":
    rendered = RAG_TEMPLATE.render(
        docs=list(enumerate(["RAG usa busca vetorial.", "ChromaDB é um vector store."], 1)),
        question="O que é RAG?",
    )
    print(rendered)
