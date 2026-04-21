"""Step-Back Prompting: reformula a pergunta em nível mais abstrato antes de responder."""

from shared.llm_client import build_client
from shared.logger import get_logger

log = get_logger(__name__)

STEP_BACK_SYSTEM = """Você é especialista em decompor perguntas complexas.
Dado uma pergunta específica, reformule-a em uma pergunta mais abstrata e de nível superior
que capture os princípios gerais necessários para responder à original.

Exemplo:
  Pergunta original: "Qual a temperatura de ebulição da água no Everest?"
  Step-back: "Como a altitude afeta a pressão atmosférica e o ponto de ebulição dos líquidos?"

Responda APENAS com a pergunta reformulada, sem explicações."""

ANSWER_SYSTEM = """Você é um especialista. Responda a pergunta original usando o contexto
do princípio geral fornecido."""


def step_back_query(question: str) -> dict:
    client = build_client()

    # Passo 1: Gerar step-back question
    messages = [{"role": "user", "content": f"Pergunta original: {question}"}]
    abstract_question = client.complete(messages, system=STEP_BACK_SYSTEM, max_tokens=200)
    log.info(f"Step-back question: {abstract_question.strip()}")

    # Passo 2: Responder a pergunta abstrata (gera contexto de princípio)
    messages2 = [{"role": "user", "content": abstract_question.strip()}]
    principle_context = client.complete(messages2, max_tokens=512)

    # Passo 3: Usar o contexto para responder a pergunta original
    final_prompt = (
        f"Contexto (princípio geral):\n{principle_context}\n\n"
        f"Com base nesse princípio, responda: {question}"
    )
    messages3 = [{"role": "user", "content": final_prompt}]
    final_answer = client.complete(messages3, max_tokens=512)

    return {
        "original_question": question,
        "step_back_question": abstract_question.strip(),
        "principle_context": principle_context,
        "final_answer": final_answer,
    }


def main() -> None:
    question = "Por que o modelo GPT-3 tem dificuldade com raciocínio de múltiplos passos?"

    result = step_back_query(question)

    print(f"PERGUNTA ORIGINAL:\n  {result['original_question']}\n")
    print(f"STEP-BACK QUESTION:\n  {result['step_back_question']}\n")
    print(f"PRINCÍPIO GERAL:\n{result['principle_context']}\n")
    print(f"RESPOSTA FINAL:\n{result['final_answer']}")


if __name__ == "__main__":
    main()
