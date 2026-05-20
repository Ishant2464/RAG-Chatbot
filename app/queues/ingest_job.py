from redis import Redis
from app.core.config import settings
from rq import Queue
from app.queues.worker_tasks import process_doc

redis_conn = Redis.from_url(settings.REDIS_URL)
q = Queue(connection=redis_conn, default_timeout=settings.RQ_JOB_TIMEOUT)


def enqueue_ingest(file_path: str) -> str:
    job = q.enqueue(process_doc, file_path, job_timeout=None)
    return job.id
