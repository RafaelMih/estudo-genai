"""Definições Pydantic para schemas de tools MCP — garante type safety nos inputs."""

from pydantic import BaseModel, Field


class EchoInput(BaseModel):
    text: str = Field(..., description="Texto a repetir")


class AddNumbersInput(BaseModel):
    a: float = Field(..., description="Primeiro número")
    b: float = Field(..., description="Segundo número")


class SearchInput(BaseModel):
    query: str = Field(..., description="Termo de busca", min_length=1)
    top_k: int = Field(default=5, ge=1, le=20, description="Número de resultados")


class FileReadInput(BaseModel):
    path: str = Field(..., description="Caminho do arquivo a ler")


def to_json_schema(model: type[BaseModel]) -> dict:
    """Converte modelo Pydantic para JSON Schema compatível com MCP."""
    schema = model.model_json_schema()
    return {
        "type": "object",
        "properties": schema.get("properties", {}),
        "required": schema.get("required", []),
    }


if __name__ == "__main__":
    import json
    for model in [EchoInput, AddNumbersInput, SearchInput]:
        print(f"\n{model.__name__}:")
        print(json.dumps(to_json_schema(model), indent=2))
