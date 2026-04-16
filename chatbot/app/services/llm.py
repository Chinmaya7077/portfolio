"""
LLM layer — uses HuggingFace Inference API via huggingface_hub client.
Free, no local setup needed. Supports streaming.
"""
from collections.abc import AsyncGenerator
from huggingface_hub import InferenceClient
from app.utils.config import get_settings
from app.utils.logger import get_logger

log = get_logger(__name__)

_client: InferenceClient | None = None


def _get_client() -> InferenceClient:
    global _client
    if _client is None:
        settings = get_settings()
        _client = InferenceClient(token=settings.huggingface_api_token)
        log.info(f"HuggingFace client initialized (model: {settings.hf_model})")
    return _client


async def generate_stream(
    system_prompt: str, user_prompt: str
) -> AsyncGenerator[str, None]:
    """Stream tokens from HuggingFace Inference API."""
    settings = get_settings()
    client = _get_client()

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    try:
        stream = client.chat.completions.create(
            model=settings.hf_model,
            messages=messages,
            max_tokens=1024,
            temperature=0.3,
            top_p=0.9,
            stream=True,
        )

        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    except Exception as e:
        error_msg = str(e)
        log.error(f"HF generation error: {error_msg}")
        if "loading" in error_msg.lower() or "503" in error_msg:
            yield "The AI model is warming up. Please try again in 30 seconds."
        else:
            yield f"Sorry, I encountered an error: {error_msg[:100]}"


async def generate_sync(system_prompt: str, user_prompt: str) -> str:
    """Non-streaming generation — returns full response."""
    settings = get_settings()
    client = _get_client()

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    try:
        response = client.chat.completions.create(
            model=settings.hf_model,
            messages=messages,
            max_tokens=1024,
            temperature=0.3,
            top_p=0.9,
        )
        return response.choices[0].message.content

    except Exception as e:
        log.error(f"HF generation error: {e}")
        return "Sorry, I encountered an error generating a response."
