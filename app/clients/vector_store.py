from qdrant_client import QdrantClient
from qdrant_client.http import models
from langchain_qdrant import QdrantVectorStore
from langchain_cohere import CohereEmbeddings
from app.core.config import QDRANT_URL, QDRANT_COLLECTION, settings

_embedding_model: CohereEmbeddings | None = None
_vector_store: QdrantVectorStore | None = None

qdrant_client = QdrantClient(
    url=QDRANT_URL,
    api_key=settings.QDRANT_API_KEY if settings.QDRANT_API_KEY else None,
)

# Create payload index for metadata.file_url metadata field for efficient filtering
try:
    qdrant_client.create_payload_index(
        collection_name=QDRANT_COLLECTION,
        field_name="metadata.file_url",  # <-- FIXED: Added 'metadata.' prefix
        field_schema=models.PayloadSchemaType.KEYWORD
    )
    print("Successfully verified Qdrant payload index for metadata.file_url.")
except Exception as e:
    pass


def get_embedding_model() -> CohereEmbeddings:
    global _embedding_model
    if _embedding_model is not None:
        return _embedding_model
    _embedding_model = CohereEmbeddings(
        cohere_api_key=settings.COHERE_API_KEY,
        model="embed-english-v3.0",
    )
    return _embedding_model


def get_vector_store() -> QdrantVectorStore:
    global _vector_store
    if _vector_store is not None:
        return _vector_store
    _vector_store = QdrantVectorStore.from_existing_collection(
        url=QDRANT_URL,
        collection_name=QDRANT_COLLECTION,
        embedding=get_embedding_model(),
        api_key=settings.QDRANT_API_KEY if settings.QDRANT_API_KEY else None,
    )
    return _vector_store


def search(query: str, file_url: str, top_k: int = 4) -> str:
    """
    Search for documents matching query and filtered by file_url.
    Only returns chunks that belong to the specified file.
    """
    vector_store = get_vector_store()
    
    # Create metadata filter to match only chunks from this file
    filter_condition = {
        "must": [
            {
                "key": "metadata.file_url",  # <-- FIXED: Added 'metadata.' prefix
                "match": {
                    "value": file_url
                }
            }
        ]
    }
    
    results = vector_store.similarity_search(
        query=query, 
        k=top_k,
        filter=filter_condition
    )
    
    context_parts = [
        f"Page Content: {r.page_content}\n"
        f"Page Number: {r.metadata.get('page_label', 'N/A')}\n"
        f"Source: {r.metadata.get('source', 'Unknown')}"
        for r in results
    ]
    return "\n\n---\n\n".join(context_parts)


def ingest_documents(chunks, collection_name: str = QDRANT_COLLECTION):
    QdrantVectorStore.from_documents(
        documents=chunks,
        embedding=get_embedding_model(),
        url=QDRANT_URL,
        collection_name=collection_name,
        api_key=settings.QDRANT_API_KEY if settings.QDRANT_API_KEY else None,
    )
