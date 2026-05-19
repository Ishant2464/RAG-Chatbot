from fastapi import FastAPI
from app.api import chat, ingest

app = FastAPI(
    title="Scalable RAG Chatbot",
    description="Document ingestion and retrieval-augmented generation API",
    version="1.0.0",
)

app.include_router(chat.router, tags=["Chat"])
app.include_router(ingest.router, tags=["Ingest"])


@app.get("/health")
def health():
    return {"status": "ok"}
