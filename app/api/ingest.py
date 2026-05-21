import os
import re
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from rq.job import Job

from app.queues.ingest_job import enqueue_ingest, redis_conn
from app.clients.supabase_client import upload_file_to_supabase

router = APIRouter()


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for Supabase storage.
    - Remove/replace special characters that cause 400 errors
    - Add UUID prefix to ensure uniqueness
    """
    # Remove extension temporarily
    name_without_ext = filename.rsplit(".", 1)[0] if "." in filename else filename
    ext = filename.rsplit(".", 1)[1] if "." in filename else ""
    
    # Replace any character that isn't alphanumeric, dot, dash, or underscore
    clean_name = re.sub(r'[^a-zA-Z0-9.\-_]', '_', name_without_ext)
    
    # Add UUID prefix for uniqueness
    unique_id = uuid.uuid4().hex[:8]
    
    return f"{unique_id}_{clean_name}.{ext}" if ext else f"{unique_id}_{clean_name}"


@router.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    """
    Upload PDF to Supabase Storage, then enqueue for processing.
    Worker will download from Supabase URL and process.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        # Read file content
        file_content = await file.read()
        print(f"[API] File received: {file.filename} ({len(file_content)} bytes)")
        
        # Sanitize filename for Supabase
        clean_filename = sanitize_filename(file.filename)
        print(f"[API] Original filename: {file.filename} → Sanitized: {clean_filename}")
        
        # Upload to Supabase Storage
        storage_url = upload_file_to_supabase(file_content, clean_filename)
        print(f"[API] File uploaded to Supabase: {storage_url}")
        
        # Enqueue job with storage URL (not local path)
        job_id = enqueue_ingest(storage_url)
        print(f"[API] Job enqueued: {job_id}")
        
    except Exception as e:
        print(f"[API] Ingestion failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

    return {"job_id": job_id, "file": file.filename, "status": "queued", "storage_url": storage_url}


@router.get("/ingest/{job_id}/status")
async def ingest_status(job_id: str):
    try:
        job = Job.fetch(job_id, connection=redis_conn)
    except Exception:
        raise HTTPException(status_code=404, detail="Job not found.")

    return {"job_id": job_id, "status": job.get_status(), "error": job.exc_info}
