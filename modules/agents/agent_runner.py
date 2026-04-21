"""CLI entry point para rodar o agente ReAct."""

import argparse

from modules.agents.react_agent import ReActAgent
from shared.logger import get_logger

log = get_logger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="Roda o agente ReAct com uma query")
    parser.add_argument("--query", required=True, help="Pergunta ou tarefa para o agente")
    parser.add_argument("--max-steps", type=int, default=8, help="Máximo de passos ReAct")
    args = parser.parse_args()

    agent = ReActAgent(max_steps=args.max_steps)
    print(f"\nExecutando agente com query: {args.query}\n{'='*60}")
    result = agent.run(args.query)
    print(f"\n{'='*60}\nResposta final:\n{result}")


if __name__ == "__main__":
    main()
