"""
config.py
Centralised settings loaded from environment variables via pydantic-settings.
All other modules import from here — never read os.environ directly.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── OpenAI ──────────────────────────────────────────────────────────────
    openai_api_key: str
    openai_model: str = "gpt-3.5-turbo"
    openai_embedding_model: str = "text-embedding-ada-002"

    # ── ChromaDB ─────────────────────────────────────────────────────────────
    chroma_persist_dir: str = "./chroma_store"
    chroma_collection_name: str = "dev_knowledge"

    # ── FastAPI ──────────────────────────────────────────────────────────────
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_env: str = "development"

    # ── RAG Settings ─────────────────────────────────────────────────────────
    top_k_results: int = 5
    chunk_size: int = 500
    chunk_overlap: int = 50

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Return a cached Settings instance (singleton pattern)."""
    return Settings()
