"""
FastAPI application entry point.
Initializes all layers: RAG, memory, tools, and routes.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import chat, health
from app.rag.retriever import get_vector_store
from app.utils.logger import get_logger

log = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize components on startup."""
    log.info("Starting Portfolio AI Chatbot...")

    # Initialize vector store (runs ingestion if needed)
    try:
        store = get_vector_store()
        count = store._collection.count()
        log.info(f"Vector store ready: {count} chunks indexed")
    except Exception as e:
        log.error(f"Vector store initialization failed: {e}")

    log.info("Chatbot ready to serve requests")
    yield
    log.info("Shutting down chatbot...")


app = FastAPI(
    title="Portfolio AI Chatbot",
    description=(
        "AI assistant for Chinmaya Ranjan Sahu's developer portfolio. "
        "Uses RAG, tool calling, and conversation memory."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(chat.router, tags=["Chat"])
app.include_router(health.router, tags=["Health"])


@app.get("/")
async def root():
    return {
        "name": "Portfolio AI Chatbot",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "chat": "POST /chat",
            "health": "GET /health",
            "suggestions": "GET /chat/suggestions",
            "history": "GET /chat/history?session_id=xxx",
        },
    }
