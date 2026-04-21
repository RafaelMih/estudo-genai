"""Compara o efeito de diferentes system prompts na mesma pergunta."""

from shared.llm_client import build_client

QUESTION = "O que é RAG?"

PERSONAS = {
    "Tutor didático": "Você é um professor universitário. Explique de forma didática com exemplos.",
    "Expert técnico": "Você é um engenheiro de ML sênior. Seja técnico e preciso, use terminologia correta.",
    "Leigo amigável": "Explique como se estivesse falando com alguém sem conhecimento técnico, usando analogias do dia a dia.",
    "Minimalista": "Responda em no máximo 2 frases.",
}


def main() -> None:
    client = build_client()
    messages = [{"role": "user", "content": QUESTION}]

    print(f'Pergunta: "{QUESTION}"\n')
    print("=" * 70)

    for persona, system_prompt in PERSONAS.items():
        print(f"\n[PERSONA: {persona}]")
        print(f"System: {system_prompt[:80]}...")
        print("-" * 40)
        response = client.complete(messages, system=system_prompt, max_tokens=512)
        print(response)
        print("=" * 70)


if __name__ == "__main__":
    main()
