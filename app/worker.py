from redis import Redis
from rq import Worker, Queue
from app.core.config import settings

redis_conn = Redis.from_url(settings.REDIS_URL)

if __name__ == "__main__":
    queue = Queue(connection=redis_conn)
    worker = Worker([queue], connection=redis_conn)
    worker.work()
