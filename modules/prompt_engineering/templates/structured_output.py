"""Prompts para forçar output estruturado (JSON e XML)."""

import json
import re

from shared.llm_client import build_client

JSON_SYSTEM = """Você é um assistente que SEMPRE responde em JSON válido, sem texto fora do JSON.
O JSON deve ter a estrutura: {"answer": "...", "confidence": 0.0-1.0, "reasoning": "..."}"""

XML_SYSTEM = """Você é um assistente que SEMPRE responde usando tags XML.
Use exatamente o formato:
<response>
  <answer>sua resposta</answer>
  <confidence>0.0-1.0</confidence>
  <reasoning>seu raciocínio</reasoning>
</response>"""


def ask_json(question: str) -> dict:
    client = build_client()
    messages = [{"role": "user", "content": question}]
    raw = client.complete(messages, system=JSON_SYSTEM, max_tokens=512)
    raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(raw)


def ask_xml(question: str) -> dict:
    client = build_client()
    messages = [{"role": "user", "content": question}]
    raw = client.complete(messages, system=XML_SYSTEM, max_tokens=512)

    def extract(tag: str) -> str:
        m = re.search(rf"<{tag}>(.*?)</{tag}>", raw, re.DOTALL)
        return m.group(1).strip() if m else ""

    return {
        "answer": extract("answer"),
        "confidence": float(extract("confidence") or 0),
        "reasoning": extract("reasoning"),
    }


def main() -> None:
    question = "Qual a capital do Brasil e por que ela foi construída?"

    print("JSON OUTPUT:")
    result = ask_json(question)
    print(json.dumps(result, ensure_ascii=False, indent=2))

    print("\nXML OUTPUT:")
    result = ask_xml(question)
    print(result)


if __name__ == "__main__":
    main()
