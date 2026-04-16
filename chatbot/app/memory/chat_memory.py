"""
Conversation memory with Redis backend and in-memory fallback.
Stores chat history per session for context-aware follow-ups.
"""
import json
from datetime import datetime
from app.utils.config import get_settings
from app.utils.logger import get_logger

log = get_logger(__name__)

# Try to connect to Redis; fall back to in-memory dict
_redis_client = None
_memory_store: dict[str, list] = {}  # fallback


def _get_redis():
    """Lazy Redis connection with graceful fallback."""
    global _redis_client
    if _redis_client is not None:
        return _redis_client

    try:
        import redis

        settings = get_settings()
        client = redis.from_url(settings.redis_url, decode_responses=True)
        client.ping()
        _redis_client = client
        log.info("Redis connected for chat memory")
        return _redis_client
    except Exception as e:
        log.warning(f"Redis unavailable ({e}), using in-memory fallback")
        return None


def _session_key(session_id: str) -> str:
    return f"chat:{session_id}"


def get_history(session_id: str, limit: int = 20) -> list[dict]:
    """Retrieve conversation history for a session."""
    r = _get_redis()

    if r:
        raw = r.lrange(_session_key(session_id), -limit, -1)
        return [json.loads(msg) for msg in raw]

    # In-memory fallback
    return _memory_store.get(session_id, [])[-limit:]


def add_message(session_id: str, role: str, content: str):
    """Add a message to the session history."""
    msg = {
        "role": role,
        "content": content,
        "timestamp": datetime.utcnow().isoformat(),
    }
    r = _get_redis()

    if r:
        r.rpush(_session_key(session_id), json.dumps(msg))
        # Keep last 50 messages per session, expire after 24h
        r.ltrim(_session_key(session_id), -50, -1)
        r.expire(_session_key(session_id), 86400)
    else:
        # In-memory fallback
        if session_id not in _memory_store:
            _memory_store[session_id] = []
        _memory_store[session_id].append(msg)
        # Cap at 50 messages
        _memory_store[session_id] = _memory_store[session_id][-50:]


def format_history_for_prompt(session_id: str, limit: int = 10) -> str:
    """Format recent chat history as a string for the LLM prompt."""
    history = get_history(session_id, limit=limit)
    if not history:
        return ""

    lines = []
    for msg in history:
        role = "User" if msg["role"] == "user" else "Assistant"
        lines.append(f"{role}: {msg['content']}")

    return "\n".join(lines)


def clear_history(session_id: str):
    """Clear conversation history for a session."""
    r = _get_redis()
    if r:
        r.delete(_session_key(session_id))
    elif session_id in _memory_store:
        del _memory_store[session_id]
