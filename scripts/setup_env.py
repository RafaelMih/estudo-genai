"""Valida que o ambiente está configurado corretamente."""

import argparse
import sys

from shared.config import settings
from shared.llm_client import ANTHROPIC_PROVIDER, OPENAI_PROVIDER, build_client


def resolve_provider(cli_provider: str | None) -> str:
    return (cli_provider or settings.llm_provider or ANTHROPIC_PROVIDER).strip().lower()


def check_dotenv() -> bool:
    from pathlib import Path

    if not Path(".env").exists():
        print("✗ .env não encontrado. Copie .env.example → .env e configure o provider desejado.")
        return False
    print("✓ .env encontrado")
    return True


def check_api_key(provider: str) -> bool:
    try:
        if provider == ANTHROPIC_PROVIDER:
            key = settings.anthropic_api_key
            if not key or key.startswith("sk-ant-..."):
                print("✗ ANTHROPIC_API_KEY inválida ou não configurada")
                return False
            print(f"✓ ANTHROPIC_API_KEY configurada ({key[:12]}...)")
            return True

        if provider == OPENAI_PROVIDER:
            key = settings.openai_api_key
            if not key or key.startswith("sk-..."):
                print("✗ OPENAI_API_KEY inválida ou não configurada")
                return False
            print(f"✓ OPENAI_API_KEY configurada ({key[:12]}...)")
            return True

        print(f"✗ Provider inválido: {provider}")
        return False
    except Exception as e:
        print(f"✗ Erro ao carregar config: {e}")
        return False


def check_api_connection(provider: str, model: str | None) -> bool:
    try:
        client = build_client(provider=provider, model=model)
        response = client.complete([{"role": "user", "content": "Diga apenas: OK"}], max_tokens=10)
        print(f"✓ Conexão com {client.provider}/{client.model}: {response.strip()}")
        return True
    except Exception as e:
        print(f"✗ Erro na conexão com API: {e}")
        return False


def check_packages(provider: str) -> bool:
    required = ["chromadb", "sentence_transformers", "rich", "pydantic"]
    if provider == ANTHROPIC_PROVIDER:
        required.insert(0, "anthropic")
    elif provider == OPENAI_PROVIDER:
        required.insert(0, "openai")

    all_ok = True
    for pkg in required:
        try:
            __import__(pkg)
            print(f"✓ {pkg}")
        except ImportError:
            print(f"✗ {pkg} não instalado — execute: pip install -r requirements.txt")
            all_ok = False
    return all_ok


def main() -> None:
    parser = argparse.ArgumentParser(description="Valida o ambiente do projeto")
    parser.add_argument("--provider", choices=[ANTHROPIC_PROVIDER, OPENAI_PROVIDER], help="Provider LLM a validar")
    parser.add_argument("--model", help="Modelo a validar")
    args = parser.parse_args()

    provider = resolve_provider(args.provider)

    print("=== Validação do Ambiente GenAI Study Project ===\n")
    print(f"Provider: {provider}")
    print(f"Modelo: {args.model or settings.llm_model or '(default do provider)'}")

    print("\n[ Pacotes Python ]")
    pkg_ok = check_packages(provider)

    print("\n[ Configuração ]")
    env_ok = check_dotenv()
    key_ok = check_api_key(provider) if env_ok else False

    print("\n[ Conectividade ]")
    api_ok = check_api_connection(provider, args.model) if key_ok else False

    print("\n" + "=" * 50)
    if all([pkg_ok, env_ok, key_ok, api_ok]):
        print("✓ Ambiente configurado corretamente!")
        print("\nPróximos passos:")
        print("  python -m modules.llm.basic_completion")
        print("  python -m scripts.ingest_docs --dir modules/rag/data/sample_docs")
    else:
        print("✗ Corrija os erros acima antes de continuar.")
        sys.exit(1)


if __name__ == "__main__":
    main()
