"""Demonstra entrada multimodal: enviar imagem ao Claude."""

import argparse
import base64
from pathlib import Path

from shared.llm_client import build_client
from shared.logger import get_logger

log = get_logger(__name__)

SUPPORTED_TYPES = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".gif": "image/gif", ".webp": "image/webp"}


def encode_image(path: Path) -> tuple[str, str]:
    """Retorna (base64_data, media_type)."""
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_TYPES:
        raise ValueError(f"Formato não suportado: {suffix}. Use: {list(SUPPORTED_TYPES)}")
    media_type = SUPPORTED_TYPES[suffix]
    data = base64.standard_b64encode(path.read_bytes()).decode("utf-8")
    return data, media_type


def describe_image(image_path: Path, prompt: str = "Descreva esta imagem detalhadamente.") -> str:
    data, media_type = encode_image(image_path)
    client = build_client()
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": data,
                    },
                },
                {"type": "text", "text": prompt},
            ],
        }
    ]
    return client.complete(messages, max_tokens=1024)


def main() -> None:
    parser = argparse.ArgumentParser(description="Envia imagem ao Claude para análise")
    parser.add_argument("--image", required=True, help="Caminho para a imagem")
    parser.add_argument("--prompt", default="Descreva esta imagem detalhadamente.", help="Pergunta sobre a imagem")
    args = parser.parse_args()

    image_path = Path(args.image)
    if not image_path.exists():
        print(f"Arquivo não encontrado: {image_path}")
        return

    log.info(f"Enviando {image_path.name} ao Claude...")
    response = describe_image(image_path, args.prompt)
    print("\nResposta:")
    print(response)


if __name__ == "__main__":
    main()
