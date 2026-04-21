"""REPL de conversa multi-turn. Demonstra gerência de histórico stateless."""

from shared.llm_client import build_client
from shared.logger import get_logger

log = get_logger(__name__)

SYSTEM = (
    "Você é um tutor de IA generativa. Ajude o usuário a aprender conceitos de genAI "
    "com exemplos práticos e claros. Seja conciso mas completo."
)


class Conversation:
    def __init__(self) -> None:
        self._messages: list[dict] = []
        self._client = build_client()

    def send(self, user_text: str) -> str:
        self._messages.append({"role": "user", "content": user_text})
        reply = self._client.complete(self._messages, system=SYSTEM, max_tokens=2048)
        self._messages.append({"role": "assistant", "content": reply})
        return reply

    def clear(self) -> None:
        self._messages.clear()
        print("[histórico limpo]")

    @property
    def turn_count(self) -> int:
        return len(self._messages) // 2


def main() -> None:
    conv = Conversation()
    print("Conversa multi-turn com Claude. Digite '/clear' para resetar, '/quit' para sair.\n")

    while True:
        try:
            user_input = input(f"[turn {conv.turn_count + 1}] Você: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSaindo...")
            break

        if not user_input:
            continue
        if user_input == "/quit":
            break
        if user_input == "/clear":
            conv.clear()
            continue

        response = conv.send(user_input)
        print(f"\nClaude: {response}\n")


if __name__ == "__main__":
    main()
