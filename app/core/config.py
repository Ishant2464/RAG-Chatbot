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

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_URL: str = "redis://valkey:6379"
    RQ_JOB_TIMEOUT: int = 300
    UPLOAD_DIR: str = "/tmp/rag_uploads"


def ensure_upload_directory(upload_dir: str) -> None:
    Path(upload_dir).mkdir(parents=True, exist_ok=True)


settings = Settings()

GEMINI_API_KEY: str = settings.GEMINI_API_KEY
QDRANT_URL: str = settings.QDRANT_URL
QDRANT_COLLECTION: str = settings.QDRANT_COLLECTION
REDIS_HOST: str = settings.REDIS_HOST
REDIS_PORT: int = settings.REDIS_PORT
UPLOAD_DIR: str = settings.UPLOAD_DIR
LLM_MODEL: str = settings.LLM_MODEL
LLM_MAX_NEW_TOKENS: int = settings.LLM_MAX_NEW_TOKENS
EMBEDDING_MODEL: str = settings.EMBEDDING_MODEL
RQ_JOB_TIMEOUT: int = settings.RQ_JOB_TIMEOUT
ensure_upload_directory(settings.UPLOAD_DIR)