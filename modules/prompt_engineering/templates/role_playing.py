"""Demonstra o efeito de personas e papéis no system prompt."""

from shared.llm_client import build_client

ROLES = {
    "Socrates": "Você é Sócrates. Responda com perguntas que levem o interlocutor à reflexão. Use o método socrático.",
    "Engenheiro de ML": "Você é um engenheiro sênior de Machine Learning. Seja técnico, cite papers quando relevante, e foque em implementação prática.",
    "Professor de ensino médio": "Você é um professor de ensino médio. Explique usando analogias simples e evite jargões técnicos.",
    "Crítico cético": "Você é um crítico cético. Questione suposições, aponte limitações e riscos. Não aceite afirmações sem evidências.",
}

QUESTION = "A IA generativa vai substituir programadores?"


def main() -> None:
    client = build_client()
    messages = [{"role": "user", "content": QUESTION}]

    print(f'Pergunta: "{QUESTION}"\n')
    for role_name, system_prompt in ROLES.items():
        print(f"\n{'=' * 60}")
        print(f"PAPEL: {role_name}")
        print("=" * 60)
        response = client.complete(messages, system=system_prompt, max_tokens=400)
        print(response)


if __name__ == "__main__":
    main()
