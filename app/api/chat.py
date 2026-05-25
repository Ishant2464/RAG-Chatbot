from collections.abc import Awaitable, Callable

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, field_validator

from app.clients.groq_client import stream_llm
from app.clients.vector_store import search
from app.services.chat_services import handle_chat

router = APIRouter()


class ChatRequest(BaseModel):
    messages: list[dict]
    file_url: str

    @field_validator("messages")
    @classmethod
    def messages_not_empty(cls, v: list[dict]) -> list[dict]:
        if not v:
            raise ValueError("Messages list cannot be empty.")
        if v[-1].get("role") != "user":
            raise ValueError("Last message must be from the user.")
        if not v[-1].get("content", "").strip():
            raise ValueError("Last user message content cannot be empty.")
        return v


def get_chat_service() -> Callable[[list[dict], str], Awaitable[dict]]:
    return handle_chat


@router.post("/chat")
async def chat(
    request: ChatRequest,
    chat_service: Callable[[list[dict], str], Awaitable[dict]] = Depends(get_chat_service),
):
    try:
        return await chat_service(request.messages, request.file_url)
    except Exception as e:
        print(f"CHAT ERROR: {e}")
        raise HTTPException(status_code=503, detail=f"Chat service error: {str(e)}")


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    try:
        query = request.messages[-1]["content"] # Extract latest user query for retrieval
        context = search(query, file_url=request.file_url, top_k=3)
        if not context.strip():
            context = "No relevant context found."
        context = context[:1200]

        async def generate():
            async for token in stream_llm(context, request.messages):
                yield token

        return StreamingResponse(generate(), media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Stream error: {str(e)}")
