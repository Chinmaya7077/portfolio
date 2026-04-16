"""
Agent layer — orchestrates RAG retrieval, tool calling, memory, and LLM.
"""
from langchain_core.tools import BaseTool
from app.services.llm import generate_stream, generate_sync
from app.rag.retriever import get_retriever
from app.tools.portfolio_tools import (
    get_github_projects,
    generate_api_example,
    explain_architecture,
)
from app.memory.chat_memory import (
    add_message,
    format_history_for_prompt,
)
from app.utils.logger import get_logger
from collections.abc import AsyncGenerator

log = get_logger(__name__)

SYSTEM_PROMPT = """You are Chinmaya's Portfolio AI Assistant — a helpful, concise, and technically accurate chatbot that answers questions about Chinmaya Ranjan Sahu's projects, skills, experience, and blog posts.

STRICT RULES:
1. ONLY answer based on the provided context, tool outputs, or conversation history.
2. If the context does not contain the answer, say "I don't have that information in my knowledge base."
3. NEVER make up facts, projects, companies, or details not present in the context.
4. Keep answers concise and technical. Use bullet points for lists.
5. When discussing code or architecture, be specific and reference actual technologies used.
6. Always maintain a professional, friendly tone.
7. For follow-up questions, use conversation history for context.
8. Do NOT repeat the question back. Jump straight to the answer."""

TOOLS: list[BaseTool] = [
    get_github_projects,
    generate_api_example,
    explain_architecture,
]


def _should_use_tool(query: str) -> BaseTool | None:
    """Determine if a query should be routed to a specific tool."""
    q = query.lower()

    if any(kw in q for kw in ["github", "repo", "repository", "source code", "link"]):
        return get_github_projects

    if any(kw in q for kw in ["code example", "api example", "show me code", "sample code", "implementation"]):
        return generate_api_example

    if any(kw in q for kw in ["architecture", "system design", "how is", "design of"]):
        return explain_architecture

    return None


def _extract_tool_input(query: str, tool: BaseTool) -> str:
    """Extract the relevant input for a tool from the user query."""
    if tool.name == "generate_api_example":
        q = query.lower()
        for topic in ["fastapi", "django", "authentication", "websocket", "redis"]:
            if topic in q:
                return topic
        return "fastapi"

    if tool.name == "explain_architecture":
        q = query.lower()
        for project in ["ezwallet", "trading", "whatsapp", "chatbot", "training", "ops"]:
            if project in q:
                return project
        return query

    return query


async def chat(query: str, session_id: str = "default") -> AsyncGenerator[str, None]:
    """
    Main chat function with streaming response.
    Routes between RAG retrieval and tool calling, with memory support.
    """
    log.info(f"[{session_id}] Query: {query}")

    # Save user message to memory
    add_message(session_id, "user", query)

    # Step 1: Check if a tool should handle this
    tool = _should_use_tool(query)
    tool_output = ""

    if tool:
        log.info(f"[{session_id}] Routing to tool: {tool.name}")
        tool_input = _extract_tool_input(query, tool)
        try:
            tool_output = tool.invoke(tool_input)
        except Exception as e:
            log.error(f"Tool {tool.name} failed: {e}")

    # Step 2: RAG retrieval for context
    retriever = get_retriever()
    docs = retriever.invoke(query)
    rag_context = "\n\n---\n\n".join(doc.page_content for doc in docs)

    # Step 3: Build conversation history
    history = format_history_for_prompt(session_id, limit=6)

    # Step 4: Construct the user prompt with context
    context_parts = []
    if rag_context:
        context_parts.append(f"RETRIEVED CONTEXT:\n{rag_context}")
    if tool_output:
        context_parts.append(f"TOOL OUTPUT ({tool.name}):\n{tool_output}")
    if history:
        context_parts.append(f"CONVERSATION HISTORY:\n{history}")

    full_context = "\n\n".join(context_parts)

    user_prompt = f"""{full_context}

USER QUESTION: {query}

Answer based ONLY on the context and tool output above. If the information is not available, say so."""

    # Step 5: Stream response from HuggingFace
    full_response = ""

    async for token in generate_stream(SYSTEM_PROMPT, user_prompt):
        full_response += token
        yield token

    # Save assistant response to memory
    add_message(session_id, "assistant", full_response)
    log.info(f"[{session_id}] Response length: {len(full_response)} chars")


async def chat_sync(query: str, session_id: str = "default") -> str:
    """Non-streaming version — collects full response."""
    chunks = []
    async for token in chat(query, session_id):
        chunks.append(token)
    return "".join(chunks)
