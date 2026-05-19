from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.clients.vector_store import ingest_documents


def process_document(file_path: str) -> None:
    print(f"[Ingest] Loading document: {file_path}")
    loader = PyPDFLoader(file_path=file_path)
    docs = loader.load()
    print(f"[Ingest] Loaded {len(docs)} pages")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    chunks = splitter.split_documents(docs)
    print(f"[Ingest] Split into {len(chunks)} chunks")

    ingest_documents(chunks)
    print(f"[Ingest] Indexed {len(chunks)} chunks into Qdrant")
