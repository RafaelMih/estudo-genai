"""Experimenta o efeito de temperature na diversidade das respostas."""

from shared.llm_client import build_client

PROMPT = "Continue esta frase de forma criativa: 'A IA generativa vai mudar o mundo porque...'"
TEMPERATURES = [0.0, 0.3, 0.7, 1.0, 1.5]
RUNS_PER_TEMP = 2


def main() -> None:
    client = build_client()
    messages = [{"role": "user", "content": PROMPT}]

    print(f'Prompt: "{PROMPT}"\n')

    for temp in TEMPERATURES:
        print(f"\n{'=' * 60}")
        print(f"TEMPERATURE = {temp}")
        print("=" * 60)
        for run in range(1, RUNS_PER_TEMP + 1):
            response = client.complete(messages, temperature=temp, max_tokens=150)
            print(f"\n  [Run {run}] {response.strip()}")

    print("\n\nObservações:")
    print("  temperature=0.0 → respostas idênticas ou muito similares (quase determinístico)")
    print("  temperature=1.0 → comportamento padrão balanceado")
    print("  temperature=1.5 → alta variabilidade, pode ser incoerente")


if __name__ == "__main__":
    main()
