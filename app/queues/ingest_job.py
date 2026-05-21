from redis import Redis
from app.core.config import settings
from rq import Queue
from app.services.ingest_service import process_document 

redis_conn = Redis.from_url(settings.REDIS_URL)
q = Queue(connection=redis_conn, default_timeout=settings.RQ_JOB_TIMEOUT)

def enqueue_ingest(storage_url: str) -> str:
    job = q.enqueue(process_document, storage_url, job_timeout=None)
    return job.id