"""CLI: roda o agente ReAct com uma query."""

import argparse

from modules.agents.react_agent import ReActAgent
from shared.logger import get_logger

log = get_logger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="Roda o agente ReAct")
    parser.add_argument("--query", required=True, help="Tarefa ou pergunta para o agente")
    parser.add_argument("--max-steps", type=int, default=8, help="Máximo de passos do loop ReAct")
    args = parser.parse_args()

    agent = ReActAgent(max_steps=args.max_steps)
    print(f"\nQuery: {args.query}")
    print("=" * 60)
    result = agent.run(args.query)
    print("\nResposta final:")
    print(result)


if __name__ == "__main__":
    main()
