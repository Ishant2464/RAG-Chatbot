from __future__ import annotations
import asyncio
from groq import Groq
from app.core.config import settings

_client: Groq | None = None

def _get_client() -> Groq:
    global _client
    if _client is not None:
        return _client
    _client = Groq(api_key=settings.GROQ_API_KEY)
    return _client

def _generate_sync(context: str, query: str) -> str:
    client = _get_client()
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant. Answer questions using only the provided context. Be concise and accurate."
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {query}"
            }
        ],
        temperature=0,
        max_tokens=512,
    )
    return response.choices[0].message.content.strip()

async def call_llm(context: str, query: str) -> str:
    return await asyncio.to_thread(_generate_sync, context, query)

from collections.abc import AsyncGenerator

async def stream_llm(context: str, query: str) -> AsyncGenerator[str, None]:
    client = _get_client()
    stream = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant. Answer questions using only the provided context. Be concise and accurate."
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {query}"
            }
        ],
        temperature=0,
        max_tokens=512,
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta is not None:
            yield delta
