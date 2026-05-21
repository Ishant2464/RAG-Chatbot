from collections.abc import Awaitable, Callable

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, field_validator

from app.clients.groq_client import stream_llm
from app.clients.vector_store import search
from app.services.chat_services import handle_chat

router = APIRouter()


class ChatRequest(BaseModel):
    query: str
    file_url: str

    @field_validator("query")
    @classmethod
    def query_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Query cannot be empty.")
        return v


def get_chat_service() -> Callable[[str, str], Awaitable[dict]]:
    return handle_chat


@router.post("/chat")
async def chat(
    request: ChatRequest,
    chat_service: Callable[[str, str], Awaitable[dict]] = Depends(get_chat_service),
):
    try:
        return await chat_service(request.query, request.file_url)
    except Exception as e:
        print(f"CHAT ERROR: {e}")
        raise HTTPException(status_code=503, detail=f"Chat service error: {str(e)}")


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    try:
        context = search(request.query, file_url=request.file_url, top_k=3)
        if not context.strip():
            context = "No relevant context found."
        context = context[:1200]

        async def generate():
            async for token in stream_llm(context, request.query):
                yield token

        return StreamingResponse(generate(), media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Stream error: {str(e)}")
