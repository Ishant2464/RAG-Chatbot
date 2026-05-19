from rq import Worker, Queue
from redis import Redis
from app.core.config import REDIS_HOST, REDIS_PORT

redis_conn = Redis(host=REDIS_HOST, port=REDIS_PORT)

if __name__ == "__main__":
    worker = Worker([Queue(connection=redis_conn)], connection=redis_conn)
    worker.work(with_scheduler=True)
