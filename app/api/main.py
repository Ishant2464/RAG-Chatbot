from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import chat, ingest

app = FastAPI(
    title="Scalable RAG Chatbot",
    description="Document ingestion and retrieval-augmented generation API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.vercel.app",
        "rag-chatbot-sage.vercel.app",
        "https://rag-chatbot-git-main-ishant2464s-projects.vercel.app/",
        "rag-chatbot-bt19wswaf-ishant2464s-projects.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, tags=["Chat"])
app.include_router(ingest.router, tags=["Ingest"])


@app.get("/health")
@app.head("/health")
def health():
    return {"status": "ok"}
