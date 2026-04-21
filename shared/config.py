from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    anthropic_api_key: str = Field(..., alias="ANTHROPIC_API_KEY")
    chroma_persist_dir: str = Field(
        default="./modules/vector_store/chroma_db",
        alias="CHROMA_PERSIST_DIR",
    )
    embedding_model: str = Field(default="all-MiniLM-L6-v2", alias="EMBEDDING_MODEL")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    tavily_api_key: str | None = Field(default=None, alias="TAVILY_API_KEY")

    model_config = {
        "env_file": str(Path(__file__).parent.parent / ".env"),
        "env_file_encoding": "utf-8",
        "populate_by_name": True,
    }

    @property
    def chroma_persist_path(self) -> Path:
        return Path(self.chroma_persist_dir)


settings = Settings()
