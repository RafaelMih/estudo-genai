"""Multi-agent: Orchestrator decompõe tarefas e delega a Workers especializados."""

from __future__ import annotations

import json

from shared.llm_client import build_client
from shared.logger import get_logger

log = get_logger(__name__)

ORCHESTRATOR_SYSTEM = """Você é um orquestrador de agentes. Dado uma tarefa complexa:
1. Decomponha-a em 2-4 subtarefas independentes
2. Para cada subtarefa, especifique qual worker deve executá-la
3. Responda com JSON no formato:
{
  "subtasks": [
    {"worker": "researcher", "task": "..."},
    {"worker": "analyst", "task": "..."},
    {"worker": "writer", "task": "..."}
  ]
}

Workers disponíveis:
- researcher: busca e coleta informações
- analyst: analisa dados e identifica padrões
- writer: redige e formata conteúdo final"""

WORKER_SYSTEMS = {
    "researcher": "Você é um pesquisador especialista. Pesquise e colete informações relevantes sobre a tarefa. Seja detalhado e cite fontes quando possível.",
    "analyst": "Você é um analista especialista. Analise as informações fornecidas e extraia insights, padrões e conclusões importantes.",
    "writer": "Você é um escritor especialista. Com base nas pesquisas e análises fornecidas, redija um texto claro, estruturado e informativo.",
}


class Worker:
    def __init__(self, role: str) -> None:
        self._role = role
        self._client = build_client()
        self._system = WORKER_SYSTEMS.get(role, "Você é um assistente especializado.")

    def execute(self, task: str, context: str = "") -> str:
        prompt = task if not context else f"Contexto anterior:\n{context}\n\nSua tarefa: {task}"
        messages = [{"role": "user", "content": prompt}]
        result = self._client.complete(messages, system=self._system, max_tokens=1024)
        log.info(f"[{self._role}] concluiu: {task[:60]}...")
        return result


class Orchestrator:
    def __init__(self) -> None:
        self._client = build_client()
        self._workers = {role: Worker(role) for role in WORKER_SYSTEMS}

    def run(self, task: str) -> str:
        log.info(f"Orquestrando: {task[:80]}")
        messages = [{"role": "user", "content": f"Tarefa: {task}"}]
        plan_raw = self._client.complete(messages, system=ORCHESTRATOR_SYSTEM, max_tokens=512)

        try:
            plan_raw = plan_raw.strip().removeprefix("```json").removesuffix("```").strip()
            plan = json.loads(plan_raw)
            subtasks = plan["subtasks"]
        except Exception:
            log.warning("Falha ao parsear plano — executando tarefa diretamente")
            return self._workers["writer"].execute(task)

        print(f"\nPlano: {len(subtasks)} subtarefas")
        accumulated_context = ""
        results = []

        for i, subtask in enumerate(subtasks, 1):
            worker_role = subtask["worker"]
            worker_task = subtask["task"]
            print(f"  [{i}] {worker_role}: {worker_task[:60]}")

            if worker_role in self._workers:
                result = self._workers[worker_role].execute(worker_task, accumulated_context)
                accumulated_context += f"\n\n[{worker_role}]: {result[:500]}"
                results.append(f"## {worker_role.title()}\n{result}")
            else:
                log.warning(f"Worker desconhecido: {worker_role}")

        return "\n\n".join(results)


def main() -> None:
    orchestrator = Orchestrator()
    task = "Crie um guia conciso sobre RAG (Retrieval-Augmented Generation): o que é, como funciona e quando usar."
    print(f"Tarefa: {task}\n")
    result = orchestrator.run(task)
    print("\n" + "=" * 60)
    print("RESULTADO FINAL:")
    print("=" * 60)
    print(result)


if __name__ == "__main__":
    main()
