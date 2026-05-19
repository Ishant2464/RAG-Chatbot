from qdrant_client import QdrantClient
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from app.core.config import QDRANT_URL, QDRANT_COLLECTION, EMBEDDING_MODEL

_embedding_model: HuggingFaceEmbeddings | None = None

qdrant_client = QdrantClient(url=QDRANT_URL)


def get_embedding_model() -> HuggingFaceEmbeddings:
    global _embedding_model

    if _embedding_model is not None:
        return _embedding_model

    try:
        _embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        return _embedding_model
    except Exception as exc:
        raise RuntimeError(
            "Failed to initialize local embedding model. "
            "Check internet access for first-time model download, verify "
            "EMBEDDING_MODEL in .env, and ensure `sentence-transformers` is installed."
        ) from exc


def get_vector_store() -> QdrantVectorStore:
    return QdrantVectorStore.from_existing_collection(
        url=QDRANT_URL,
        collection_name=QDRANT_COLLECTION,
        embedding=get_embedding_model(),
    )


def search(query: str, top_k: int = 4) -> str:
    vector_store = get_vector_store()
    results = vector_store.similarity_search(query=query, k=top_k)

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
    )
