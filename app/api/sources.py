from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from app.clients.vector_store import search_with_sources

router = APIRouter()

class SourcesRequest(BaseModel):
    query: str
    file_url: str

    @field_validator("query")
    @classmethod
    def query_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Query cannot be empty.")
        return v

@router.post("/chat/sources")
async def get_sources(request: SourcesRequest):
    try:
        result = search_with_sources(
            query=request.query,
            file_url=request.file_url,
            top_k=3
        )
        return {"sources": result["sources"]}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Sources error: {str(e)}")