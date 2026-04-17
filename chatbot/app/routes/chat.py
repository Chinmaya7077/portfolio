"""
API routes for the chatbot.
Supports streaming via SSE (Server-Sent Events) and non-streaming mode.
"""
import uuid
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from app.services.agent import chat, chat_sync
from app.memory.chat_memory import get_history, clear_history
from app.utils.logger import get_logger

log = get_logger(__name__)

router = APIRouter()


class ChatRequest(BaseModel):
    query: str
    session_id: str | None = None
    stream: bool = True


class ChatResponse(BaseModel):
    response: str
    session_id: str


SUGGESTED_QUESTIONS = [
    "What projects have you built?",
    "What is your tech stack?",
    "Tell me about your experience",
    "What is your education?",
]


@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint.
    - stream=true (default): Returns Server-Sent Events for token-by-token streaming
    - stream=false: Returns complete JSON response
    """
    session_id = request.session_id or str(uuid.uuid4())
    log.info(f"Chat request: session={session_id}, stream={request.stream}")

    if request.stream:
        # SSE streaming response
        async def event_generator():
            async for token in chat(request.query, session_id):
                yield {"event": "token", "data": token}
            yield {"event": "done", "data": session_id}

        return EventSourceResponse(event_generator())
    else:
        # Synchronous full response
        response = await chat_sync(request.query, session_id)
        return ChatResponse(response=response, session_id=session_id)


@router.get("/chat/history")
async def get_chat_history(session_id: str = Query(...)):
    """Retrieve conversation history for a session."""
    history = get_history(session_id)
    return {"session_id": session_id, "messages": history}


@router.delete("/chat/history")
async def delete_chat_history(session_id: str = Query(...)):
    """Clear conversation history for a session."""
    clear_history(session_id)
    return {"message": f"History cleared for session {session_id}"}


@router.get("/chat/suggestions")
async def get_suggestions():
    """Return suggested questions for the chat widget."""
    return {"suggestions": SUGGESTED_QUESTIONS}
