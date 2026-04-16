"""
Centralized configuration loaded from environment variables.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # HuggingFace
    huggingface_api_token: str = ""
    hf_model: str = "Qwen/Qwen2.5-7B-Instruct"

    # ChromaDB
    chroma_persist_dir: str = "./db"

    # Data
    data_dir: str = "./data"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # RAG
    chunk_size: int = 600
    chunk_overlap: int = 100
    retriever_top_k: int = 4

    # Logging
    log_level: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


@lru_cache()
def get_settings() -> Settings:
    return Settings()
