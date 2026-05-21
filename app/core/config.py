from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    LLM_MODEL: str = "distilgpt2"
    LLM_MAX_NEW_TOKENS: int = 150
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION: str = "rag_docs"
    QDRANT_API_KEY: str = ""
    COHERE_API_KEY: str = ""

    REDIS_URL: str = "redis://localhost:6379"
    RQ_JOB_TIMEOUT: int = 300
    UPLOAD_DIR: str = "/tmp/rag_uploads"
    
    # Supabase Storage
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_BUCKET: str = "rag-docs"


def ensure_upload_directory(upload_dir: str) -> None:
    Path(upload_dir).mkdir(parents=True, exist_ok=True)


settings = Settings()

# Validate required environment variables on startup
if not settings.GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is required")
if not settings.QDRANT_URL:
    raise ValueError("QDRANT_URL environment variable is required")

QDRANT_URL: str = settings.QDRANT_URL
QDRANT_COLLECTION: str = settings.QDRANT_COLLECTION
UPLOAD_DIR: str = settings.UPLOAD_DIR
LLM_MODEL: str = settings.LLM_MODEL
LLM_MAX_NEW_TOKENS: int = settings.LLM_MAX_NEW_TOKENS
EMBEDDING_MODEL: str = settings.EMBEDDING_MODEL
RQ_JOB_TIMEOUT: int = settings.RQ_JOB_TIMEOUT
ensure_upload_directory(settings.UPLOAD_DIR)
