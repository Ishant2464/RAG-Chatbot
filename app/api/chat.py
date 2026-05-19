from collections.abc import Awaitable, Callable

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator

from app.services.chat_services import handle_chat

router = APIRouter()


class ChatRequest(BaseModel):
    query: str

    @field_validator("query")
    @classmethod
    def query_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Query cannot be empty.")
        return v


def get_chat_service() -> Callable[[str], Awaitable[dict]]:
    return handle_chat


@router.post("/chat")
async def chat(
    request: ChatRequest,
    chat_service: Callable[[str], Awaitable[dict]] = Depends(get_chat_service),
):
    try:
        return await chat_service(request.query)
    except Exception as e:
        print(f"CHAT ERROR: {e}")
        raise HTTPException(status_code=503, detail=f"Chat service error: {str(e)}")
