"""
Data ingestion pipeline.
Loads documents from data/, chunks them, and stores embeddings in ChromaDB.
"""
import os
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from app.rag.embeddings import get_embedding_model
from app.utils.config import get_settings
from app.utils.logger import get_logger

log = get_logger(__name__)


def load_documents(data_dir: str) -> list:
    """Load all .txt files from data directory and subdirectories."""
    docs = []

    # Walk through all subdirectories and load .txt files
    for root, _dirs, files in os.walk(data_dir):
        for filename in files:
            if filename.endswith(".txt"):
                filepath = os.path.join(root, filename)
                try:
                    loader = TextLoader(filepath, encoding="utf-8")
                    loaded = loader.load()
                    # Tag each doc with its source category
                    rel_path = os.path.relpath(filepath, data_dir)
                    for doc in loaded:
                        doc.metadata["source"] = rel_path
                        doc.metadata["category"] = rel_path.split(os.sep)[0]
                    docs.extend(loaded)
                    log.info(f"Loaded: {rel_path}")
                except Exception as e:
                    log.error(f"Failed to load {filepath}: {e}")

    log.info(f"Total documents loaded: {len(docs)}")
    return docs


def chunk_documents(docs: list) -> list:
    """Split documents into chunks optimized for retrieval."""
    settings = get_settings()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )
    chunks = splitter.split_documents(docs)
    log.info(f"Created {len(chunks)} chunks from {len(docs)} documents")
    return chunks


def create_vector_store(chunks: list) -> Chroma:
    """Create or update ChromaDB vector store with document chunks."""
    settings = get_settings()
    embeddings = get_embedding_model()

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=settings.chroma_persist_dir,
        collection_name="portfolio",
    )

    log.info(
        f"Vector store created with {len(chunks)} chunks "
        f"at {settings.chroma_persist_dir}"
    )
    return vector_store


def run_ingestion() -> Chroma:
    """Full ingestion pipeline: load -> chunk -> embed -> store."""
    settings = get_settings()
    data_dir = settings.data_dir

    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    docs = load_documents(data_dir)
    if not docs:
        raise ValueError("No documents found to ingest")

    chunks = chunk_documents(docs)
    vector_store = create_vector_store(chunks)
    return vector_store


if __name__ == "__main__":
    run_ingestion()
    print("Ingestion complete.")
