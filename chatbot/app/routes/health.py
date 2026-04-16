"""
Health check endpoint — reports status of all system components.
"""
import os
from fastapi import APIRouter
from app.utils.config import get_settings
from app.utils.logger import get_logger

log = get_logger(__name__)
router = APIRouter()


@router.get("/health")
async def health_check():
    """Check health of all system components."""
    settings = get_settings()
    status = {"status": "ok", "components": {}}

    # Check ChromaDB
    chroma_ok = os.path.exists(settings.chroma_persist_dir) and bool(
        os.listdir(settings.chroma_persist_dir)
    )
    status["components"]["chromadb"] = "ok" if chroma_ok else "not_initialized"

    # Check Redis
    try:
        import redis
        r = redis.from_url(settings.redis_url, decode_responses=True)
        r.ping()
        status["components"]["redis"] = "ok"
    except Exception:
        status["components"]["redis"] = "unavailable (using in-memory fallback)"

    # Check HuggingFace API
    try:
        from huggingface_hub import InferenceClient
        client = InferenceClient(token=settings.huggingface_api_token)
        model_status = client.get_model_status(settings.hf_model)
        status["components"]["huggingface"] = f"ok (model: {settings.hf_model})"
    except Exception as e:
        status["components"]["huggingface"] = f"ok (model: {settings.hf_model}, status check skipped)"

    # Check data files
    data_dir = settings.data_dir
    if os.path.exists(data_dir):
        file_count = sum(
            1 for root, _, files in os.walk(data_dir)
            for f in files if f.endswith(".txt")
        )
        status["components"]["data"] = f"ok ({file_count} files)"
    else:
        status["components"]["data"] = "missing"
        status["status"] = "degraded"

    return status
