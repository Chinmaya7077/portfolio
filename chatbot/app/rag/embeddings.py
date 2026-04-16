"""
Embedding model wrapper using sentence-transformers.
Uses all-MiniLM-L6-v2 — a fast, free, local embedding model.
"""
from langchain_huggingface import HuggingFaceEmbeddings
from functools import lru_cache
from app.utils.logger import get_logger

log = get_logger(__name__)


@lru_cache()
def get_embedding_model() -> HuggingFaceEmbeddings:
    """Load the sentence-transformer model once and cache it."""
    log.info("Loading embedding model: all-MiniLM-L6-v2")
    return HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
