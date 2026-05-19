from __future__ import annotations

import asyncio
import threading
from typing import Any

from transformers import pipeline

from app.core.config import LLM_MAX_NEW_TOKENS, LLM_MODEL

_pipeline_lock = threading.Lock()
_text_generator: Any | None = None


def _get_text_generator():
    global _text_generator

    if _text_generator is not None:
        return _text_generator

    with _pipeline_lock:
        if _text_generator is not None:
            return _text_generator

        try:
            _text_generator = pipeline("text2text-generation", model=LLM_MODEL)
        except Exception as exc:
            raise RuntimeError(
                "Failed to initialize local Hugging Face text-generation model. "
                "Check internet access for first-time model download, verify LLM_MODEL in .env, "
                "and ensure `transformers` + `torch` are installed in the container image."
            ) from exc

        return _text_generator


def _generate_answer_sync(context: str, query: str) -> str:
    generator = _get_text_generator()

    context = context[:1500]

    prompt = f"""
    Answer the question using the context below.

    Context:
    {context}

    Question:
    {query}

    Answer:
    """
    print("PROMPT PREVIEW:", prompt[:300])
    
    try:
        result = generator(
            prompt,
            max_new_tokens=LLM_MAX_NEW_TOKENS,
            do_sample=False,
            num_return_sequences=1,
        )
    except TypeError:
        result = generator(
            prompt,
            max_length=len(prompt) + LLM_MAX_NEW_TOKENS,
            do_sample=False,
            num_return_sequences=1,
        )

    return result[0]["generated_text"].strip()

async def call_llm(context: str, query: str) -> str:
    return await asyncio.to_thread(_generate_answer_sync, context, query)
