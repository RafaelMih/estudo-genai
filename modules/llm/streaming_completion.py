"""Demonstra streaming de tokens com rich.live."""

from rich.live import Live
from rich.text import Text

from shared.llm_client import build_client
from shared.logger import get_logger

log = get_logger(__name__)


def stream_response(user_message: str, system: str = "") -> str:
    client = build_client()
    messages = [{"role": "user", "content": user_message}]
    full_text = ""

    with Live(Text(""), refresh_per_second=20) as live:
        for token in client.stream(messages, system=system):
            full_text += token
            live.update(Text(full_text))

    return full_text


def main() -> None:
    system = "Você é um assistente especializado em IA. Responda de forma detalhada."
    question = "Explique como funciona o mecanismo de atenção (attention) em Transformers, passo a passo."

    print("\nStreaming resposta do provider configurado...\n")
    print("=" * 60)
    response = stream_response(question, system=system)
    print("=" * 60)
    print(f"\n[Total de caracteres: {len(response)}]")


if __name__ == "__main__":
    main()
