import requests
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.clients.vector_store import ingest_documents


def process_document(storage_url: str) -> None:
    """
    Download PDF from Supabase storage URL and process it.
    Tags all chunks with the file_url metadata for isolated retrieval.
    """
    print(f"[Ingest] Downloading document from: {storage_url}")
    
    try:
        # Download PDF from Supabase storage URL
        response = requests.get(storage_url)
        response.raise_for_status()
        
        # Load PDF from bytes using PyPDFLoader with BytesIO
        pdf_bytes = response.content
        
        # Use PyPDFLoader with temporary local file
        # (PyPDFLoader requires a file path, so we'll write to temp and read)
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
            tmp_file.write(pdf_bytes)
            tmp_path = tmp_file.name
        
        loader = PyPDFLoader(file_path=tmp_path)
        docs = loader.load()
        print(f"[Ingest] Loaded {len(docs)} pages")
        
        # Tag each document with the storage URL for retrieval filtering
        for doc in docs:
            doc.metadata["file_url"] = storage_url
        
        # Clean up temp file
        import os
        os.unlink(tmp_path)
        
    except Exception as e:
        print(f"[Ingest] Failed to download/load document: {str(e)}")
        raise

    # Increased chunk size to 2000 for better context retention
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200,
    )
    chunks = splitter.split_documents(docs)
    print(f"[Ingest] Split into {len(chunks)} chunks")

    ingest_documents(chunks)
    print(f"[Ingest] Indexed {len(chunks)} chunks into Qdrant")
