"""
Health check endpoint for worker service.
Verifies Redis connection is alive.
"""
from fastapi import FastAPI
from redis import Redis
from app.core.config import settings

app = FastAPI(title="Worker Health Check")


@app.get("/health")
def health():
    """
    Health check endpoint.
    Verifies RQ worker can connect to Redis.
    """
    try:
        redis_conn = Redis.from_url(settings.REDIS_URL)
        redis_conn.ping()
        return {
            "status": "worker-ok",
            "redis": "connected",
            "service": "rag-worker"
        }
    except Exception as e:
        print(f"[Health] Redis connection failed: {str(e)}")
        return {
            "status": "worker-degraded",
            "redis": "disconnected",
            "error": str(e),
            "service": "rag-worker"
        }, 503


@app.head("/health")
def health_head():
    """HEAD request support for health checks."""
    try:
        redis_conn = Redis.from_url(settings.REDIS_URL)
        redis_conn.ping()
        return {}
    except:
        return {}, 503
