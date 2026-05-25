from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import chat, ingest, sources, suggestions

app = FastAPI(
    title="Scalable RAG Chatbot",
    description="Document ingestion and retrieval-augmented generation API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://rag-chatbot-sage.vercel.app", 
        "https://rag-chatbot-git-main-ishant2464s-projects.vercel.app",
        "https://rag-chatbot-bt19wswaf-ishant2464s-projects.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, tags=["Chat"])
app.include_router(ingest.router, tags=["Ingest"])
app.include_router(sources.router, tags=["Sources"])
app.include_router(suggestions.router, tags=["Suggestions"])


@app.get("/health")
@app.head("/health")
def health():
    return {"status": "ok"}
