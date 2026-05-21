from supabase import create_client
from app.core.config import settings

_supabase_client = None


def get_supabase_client():
    """Get or create Supabase client."""
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client
    
    if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
        raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY environment variables are required")
    
    _supabase_client = create_client(
        supabase_url=settings.SUPABASE_URL,
        supabase_key=settings.SUPABASE_ANON_KEY
    )
    return _supabase_client


def upload_file_to_supabase(file_content: bytes, filename: str) -> str:
    """
    Upload file to Supabase storage.
    Returns the public URL of the uploaded file.
    """
    client = get_supabase_client()
    
    try:
        # Upload to bucket
        response = client.storage.from_(settings.SUPABASE_BUCKET).upload(
            path=filename,
            file=file_content,
            file_options={"content-type": "application/pdf"}
        )
        
        print(f"[Supabase] Uploaded: {filename}")
        
        # Generate public URL
        public_url = client.storage.from_(settings.SUPABASE_BUCKET).get_public_url(filename)
        print(f"[Supabase] Public URL: {public_url}")
        
        return public_url
    
    except Exception as e:
        print(f"[Supabase] Upload failed: {str(e)}")
        raise
