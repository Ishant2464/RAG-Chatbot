import os

from app.services.ingest_service import process_document


def process_doc(file_path: str) -> None:
    if not os.path.isfile(file_path):
        raise FileNotFoundError(
            f"Ingestion file not found at worker path: {file_path}. "
            "Verify UPLOAD_DIR matches the shared Docker volume mount (expected /tmp/rag_uploads)."
        )

    process_document(file_path)
