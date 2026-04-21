"""Valida que o ambiente está configurado corretamente."""

import sys


def check_dotenv() -> bool:
    from pathlib import Path

    if not Path(".env").exists():
        print("✗ .env não encontrado. Copie .env.example → .env e adicione ANTHROPIC_API_KEY")
        return False
    print("✓ .env encontrado")
    return True


def check_api_key() -> bool:
    try:
        from shared.config import settings

        key = settings.anthropic_api_key
        if not key or key.startswith("sk-ant-..."):
            print("✗ ANTHROPIC_API_KEY inválida ou não configurada")
            return False
        print(f"✓ ANTHROPIC_API_KEY configurada ({key[:12]}...)")
        return True
    except Exception as e:
        print(f"✗ Erro ao carregar config: {e}")
        return False


def check_api_connection() -> bool:
    try:
        from shared.llm_client import build_client

        client = build_client()
        response = client.complete([{"role": "user", "content": "Diga apenas: OK"}], max_tokens=10)
        print(f"✓ Conexão com Anthropic API: {response.strip()}")
        return True
    except Exception as e:
        print(f"✗ Erro na conexão com API: {e}")
        return False


def check_packages() -> bool:
    required = ["anthropic", "chromadb", "sentence_transformers", "rich", "pydantic"]
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
    print("=== Validação do Ambiente GenAI Study Project ===\n")

    print("[ Pacotes Python ]")
    pkg_ok = check_packages()

    print("\n[ Configuração ]")
    env_ok = check_dotenv()
    key_ok = check_api_key() if env_ok else False

    print("\n[ Conectividade ]")
    api_ok = check_api_connection() if key_ok else False

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
