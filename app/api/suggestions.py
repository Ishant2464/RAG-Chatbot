from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.clients.groq_client import generate_suggestions

router = APIRouter()

class SuggestionsRequest(BaseModel):
    messages: list[dict]
    file_url: str

@router.post("/chat/suggestions")
async def get_suggestions(request: SuggestionsRequest):
    try:
        suggestions = await generate_suggestions(request.messages)
        return {"suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Suggestions error: {str(e)}")