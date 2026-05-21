from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from langchain_community.embeddings import FastEmbedEmbeddings
from app.core.config import QDRANT_URL, QDRANT_COLLECTION, EMBEDDING_MODEL, settings

_embedding_model: FastEmbedEmbeddings | None = None
_vector_store: QdrantVectorStore | None = None

qdrant_client = QdrantClient(
    url=QDRANT_URL,
    api_key=settings.QDRANT_API_KEY if settings.QDRANT_API_KEY else None,
)


def get_embedding_model() -> FastEmbedEmbeddings:
    global _embedding_model
    if _embedding_model is not None:
        return _embedding_model
    try:
        _embedding_model = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")
        return _embedding_model
    except Exception as exc:
        raise RuntimeError(
            "Failed to initialize FastEmbed embedding model. "
            "Ensure qdrant-client[fastembed] is installed."
        ) from exc


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
                "key": "file_url",
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
