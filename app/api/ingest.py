import os
import shutil
from collections.abc import Callable
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from rq.job import Job

from app.queues.ingest_job import enqueue_ingest, redis_conn
from app.core.config import UPLOAD_DIR

router = APIRouter()


def get_enqueue_service() -> Callable[[str], str]:
    return enqueue_ingest


@router.post("/ingest")
async def ingest(
    file: UploadFile = File(...),
    enqueue_service: Callable[[str], str] = Depends(get_enqueue_service),
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        dest_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        job_id = enqueue_service(dest_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue ingestion job: {str(e)}")

    return {"job_id": job_id, "file": file.filename, "status": "queued"}


@router.get("/ingest/{job_id}/status")
async def ingest_status(job_id: str):
    try:
        job = Job.fetch(job_id, connection=redis_conn)
    except Exception:
        raise HTTPException(status_code=404, detail="Job not found.")

    return {"job_id": job_id, "status": job.get_status(), "error": job.exc_info}
