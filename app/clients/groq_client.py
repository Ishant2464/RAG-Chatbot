from __future__ import annotations
import asyncio
import json
from groq import Groq
from app.core.config import settings

_client: Groq | None = None

def _get_client() -> Groq:
    global _client
    if _client is not None:
        return _client
    _client = Groq(api_key=settings.GROQ_API_KEY)
    return _client

def _generate_sync(context: str, messages: list[dict]) -> str:
    client = _get_client()

    llm_messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant for a document Q&A chatbot. Follow these rules:\n"
                "1. FIRST, try to answer the question using the provided document context.\n"
                "2. If the document context contains relevant information, use it and cite which parts you're referencing.\n"
                "3. If the document context does NOT contain enough information to answer the question, clearly state: "
                "'This information is not covered in the uploaded document.' "
                "Then provide a helpful answer from your general knowledge, prefixed with: "
                "'Based on general knowledge:'\n"
                "4. Be concise, accurate, and helpful. Always prioritize document context when available."
            )
        }
    ]

    for message in messages[:-1]:
        llm_messages.append({
            "role": message["role"],
            "content": message["content"]
        })

    last_user_msg = messages[-1]["content"]
    llm_messages.append({
        "role": "user",
        "content": f"Context from document:\n{context}\n\nQuestion: {last_user_msg}"
    })

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=llm_messages,
        temperature=0,
        max_tokens=1024,
    )
    return response.choices[0].message.content.strip()

async def call_llm(context: str, messages: list[dict]) -> str:
    return await asyncio.to_thread(_generate_sync, context, messages)

from collections.abc import AsyncGenerator

async def stream_llm(context: str, messages: list[dict]) -> AsyncGenerator[str, None]:
    client = _get_client()

    llm_messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant for a document Q&A chatbot. Follow these rules:\n"
                "1. FIRST, try to answer the question using the provided document context.\n"
                "2. If the document context contains relevant information, use it and cite which parts you're referencing.\n"
                "3. If the document context does NOT contain enough information to answer the question, clearly state: "
                "'This information is not covered in the uploaded document.' "
                "Then provide a helpful answer from your general knowledge, prefixed with: "
                "'Based on general knowledge:'\n"
                "4. Be concise, accurate, and helpful. Always prioritize document context when available."
            )
        }
    ]

    for message in messages[:-1]:
        llm_messages.append({
            "role": message["role"],
            "content": message["content"]
        })

    last_user_msg = messages[-1]["content"]
    llm_messages.append({
        "role": "user",
        "content": f"Context from document:\n{context}\n\nQuestion: {last_user_msg}"
    })

    stream = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=llm_messages,
        temperature=0,
        max_tokens=1024,
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta is not None:
            yield delta

def _generate_suggestions_sync(messages: list[dict]) -> list[str]:
    client = _get_client()
    
    # Take last 6 messages for context
    recent = messages[-6:] if len(messages) > 6 else messages
    
    # Build condensed conversation summary
    summary = ""
    for msg in recent:
        role = msg.get("role", "unknown").capitalize()
        content = msg.get("content", "")
        truncated = content[:200] if len(content) > 200 else content
        summary += f"{role}: {truncated}\n"
    
    llm_messages = [
        {
            "role": "system",
            "content": (
                "You generate follow-up questions for a document Q&A chatbot. Based on the conversation so far, "
                "suggest exactly 3 short, specific follow-up questions the user might want to ask next. "
                "Each question should be different and explore a new angle. "
                "Return ONLY a JSON array of 3 strings, nothing else. "
                "Example: [\"What are the key findings?\", \"How does this compare to previous results?\", \"What methodology was used?\"]"
            )
        },
        {
            "role": "user",
            "content": f"Conversation so far:\n{summary}\n\nGenerate 3 follow-up questions."
        }
    ]
    
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=llm_messages,
        temperature=0.7,
        max_tokens=200,
    )
    
    raw = response.choices[0].message.content.strip()
    
    # Try to parse as JSON
    try:
        suggestions = json.loads(raw)
        if isinstance(suggestions, list) and len(suggestions) >= 1:
            return [str(s) for s in suggestions[:3]]
    except json.JSONDecodeError:
        pass
    
    # Fallback: split by newlines and filter lines with '?'
    import re
    lines = raw.split('\n')
    questions = [re.sub(r'[^\w\s?.!]', '', line).strip() for line in lines if '?' in line]
    questions = [q for q in questions if q]
    if len(questions) >= 1:
        return questions[:3]
    
    # Last resort: default questions
    return [
        "Tell me more about this topic",
        "What are the key takeaways?",
        "Can you summarize the main points?"
    ]

async def generate_suggestions(messages: list[dict]) -> list[str]:
    return await asyncio.to_thread(_generate_suggestions_sync, messages)
