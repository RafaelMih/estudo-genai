"""Demonstra a chamada mínima ao Anthropic SDK."""

from shared.llm_client import build_client
from shared.llm_interface import LLM
from shared.logger import get_logger

log = get_logger(__name__)


def complete(user_message: str, system: str = "", client: LLM | None = None) -> str:
    client = client or build_client()
    messages = [{"role": "user", "content": user_message}]
    return client.complete(messages, system=system)


def main() -> None:
    system = "Você é um assistente de estudos especializado em IA generativa. Responda de forma didática."
    question = "O que é um Large Language Model? Explique em 3 parágrafos."

    log.info("Enviando mensagem ao Claude...")
    response = complete(question, system=system)

    print("\n" + "=" * 60)
    print("PERGUNTA:", question)
    print("=" * 60)
    print("RESPOSTA:")
    print(response)
    print("=" * 60)


if __name__ == "__main__":
    main()
