from collections.abc import Awaitable, Callable
from fastapi import APIRouter, Depends
from app.services.chat_services import handle_chat

router = APIRouter()


def get_chat_service() -> Callable[[str], Awaitable[dict]]:
    return handle_chat


@router.post("/chat")
async def chat(
    query: str,
    chat_service: Callable[[str], Awaitable[dict]] = Depends(get_chat_service),
):
    return await chat_service(query)
