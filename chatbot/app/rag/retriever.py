"""
RAG retriever that loads ChromaDB and returns relevant document chunks.
"""
import os
from langchain_chroma import Chroma
from langchain_core.retrievers import BaseRetriever
from app.rag.embeddings import get_embedding_model
from app.rag.ingest import run_ingestion
from app.utils.config import get_settings
from app.utils.logger import get_logger

log = get_logger(__name__)

_vector_store: Chroma | None = None


def get_vector_store() -> Chroma:
    """Get or create the ChromaDB vector store."""
    global _vector_store

    if _vector_store is not None:
        return _vector_store

    settings = get_settings()
    persist_dir = settings.chroma_persist_dir

    # If DB exists, load it; otherwise run ingestion
    if os.path.exists(persist_dir) and os.listdir(persist_dir):
        log.info(f"Loading existing vector store from {persist_dir}")
        _vector_store = Chroma(
            persist_directory=persist_dir,
            embedding_function=get_embedding_model(),
            collection_name="portfolio",
        )
    else:
        log.info("No existing vector store found, running ingestion...")
        _vector_store = run_ingestion()

    return _vector_store


def get_retriever() -> BaseRetriever:
    """Create a retriever with top-k similarity search."""
    settings = get_settings()
    store = get_vector_store()

    retriever = store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": settings.retriever_top_k},
    )
    log.info(f"Retriever ready (top_k={settings.retriever_top_k})")
    return retriever


def query_similar(query: str, k: int = 4) -> list[dict]:
    """Direct similarity search — useful for debugging."""
    store = get_vector_store()
    results = store.similarity_search_with_score(query, k=k)
    return [
        {
            "content": doc.page_content,
            "metadata": doc.metadata,
            "score": float(score),
        }
        for doc, score in results
    ]
