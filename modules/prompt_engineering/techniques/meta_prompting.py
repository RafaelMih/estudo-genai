"""Meta-prompting: usa o LLM para melhorar seu próprio prompt."""

from shared.llm_client import build_client
from shared.logger import get_logger

log = get_logger(__name__)

META_SYSTEM = """Você é um especialista em engenharia de prompts para LLMs.
Analise o prompt fornecido e crie uma versão melhorada que:
1. Seja mais específica e clara
2. Inclua instruções de formato de saída
3. Adicione contexto relevante
4. Use técnicas como few-shot ou CoT se adequado

Responda APENAS com o prompt melhorado, sem explicações sobre as mudanças."""


def improve_prompt(original_prompt: str, task_description: str = "") -> dict:
    client = build_client()

    meta_input = f"""Tarefa: {task_description}

Prompt original:
{original_prompt}

Crie uma versão melhorada deste prompt:"""

    messages = [{"role": "user", "content": meta_input}]
    improved = client.complete(messages, system=META_SYSTEM, max_tokens=1024)

    # Executa ambos os prompts para comparar
    test_question = "O que é RAG e como ele melhora a qualidade das respostas de LLMs?"

    msg_original = [{"role": "user", "content": original_prompt.replace("{question}", test_question)}]
    response_original = client.complete(msg_original, max_tokens=512)

    improved_with_q = improved.replace("{question}", test_question) if "{question}" in improved else improved + f"\n\nPergunta: {test_question}"
    msg_improved = [{"role": "user", "content": improved_with_q}]
    response_improved = client.complete(msg_improved, max_tokens=512)

    return {
        "original_prompt": original_prompt,
        "improved_prompt": improved,
        "test_question": test_question,
        "response_original": response_original,
        "response_improved": response_improved,
    }


def main() -> None:
    original = "Responda a pergunta: {question}"

    result = improve_prompt(
        original_prompt=original,
        task_description="Sistema de Q&A sobre conceitos de IA generativa"
    )

    print("PROMPT ORIGINAL:")
    print(f"  {result['original_prompt']}\n")
    print("PROMPT MELHORADO:")
    print(result["improved_prompt"])
    print("\n" + "=" * 60)
    print(f"TESTE com: '{result['test_question']}'\n")
    print("Resposta com prompt original:")
    print(result["response_original"][:400])
    print("\nResposta com prompt melhorado:")
    print(result["response_improved"][:400])


if __name__ == "__main__":
    main()
