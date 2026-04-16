"""
Standalone ingestion script.
Run this to (re)build the vector database from data/ files.

Usage: python ingest.py
"""
import sys
import os

# Ensure app modules are importable
sys.path.insert(0, os.path.dirname(__file__))

from app.rag.ingest import run_ingestion
from app.utils.config import get_settings


def main():
    settings = get_settings()
    print(f"Data directory: {settings.data_dir}")
    print(f"ChromaDB directory: {settings.chroma_persist_dir}")
    print(f"Chunk size: {settings.chunk_size}, overlap: {settings.chunk_overlap}")
    print("-" * 50)

    store = run_ingestion()
    count = store._collection.count()
    print("-" * 50)
    print(f"Done! {count} chunks stored in ChromaDB.")
    print("You can now start the server with: uvicorn app.main:app --reload")


if __name__ == "__main__":
    main()
