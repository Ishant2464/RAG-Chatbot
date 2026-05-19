# Scalable RAG Chatbot

A production-style Retrieval-Augmented Generation (RAG) system that lets you upload PDF documents and ask questions about them. Built with a focus on clean architecture, async processing, and real-world engineering patterns.

---

## What It Does

1. You upload a PDF via the `/ingest` endpoint
2. The system parses, chunks, and embeds the document in the background
3. You ask a question via `/chat`
4. The system retrieves semantically relevant chunks from the vector database and generates a grounded answer using an LLM

---

## Architecture

```
┌─────────────┐     POST /ingest      ┌─────────────────┐
│   Client    │ ───────────────────► │   FastAPI App   │
│  (Browser / │                       │                 │
│   Swagger)  │     POST /chat        │  - Validates    │
│             │ ───────────────────► │  - Enqueues     │
└─────────────┘                       │  - Retrieves    │
                                       │  - Responds     │
                                       └────────┬────────┘
                                                │
                          ┌─────────────────────┼──────────────────────┐
                          │                     │                      │
                          ▼                     ▼                      ▼
                   ┌─────────────┐      ┌─────────────┐      ┌──────────────┐
                   │   Valkey    │      │   Qdrant    │      │  Groq API    │
                   │  (Redis)    │      │ (Vector DB) │      │  (LLM)       │
                   │             │      │             │      │              │
                   │  Job Queue  │      │  Embeddings │      │ llama-3.1    │
                   └──────┬──────┘      │  + Search   │      └──────────────┘
                          │             └─────────────┘
                          ▼
                   ┌─────────────┐
                   │   Worker    │
                   │  (RQ)       │
                   │             │
                   │ - PDF parse │
                   │ - Chunk     │
                   │ - Embed     │
                   │ - Store     │
                   └─────────────┘
```

### Services

| Service | Technology | Role |
|---|---|---|
| **API** | FastAPI + Uvicorn | HTTP endpoints, request handling |
| **Worker** | RQ (Redis Queue) | Background PDF processing |
| **Vector DB** | Qdrant | Embedding storage + semantic search |
| **Queue/Cache** | Valkey (Redis-compatible) | Job queue broker |
| **Embeddings** | FastEmbed (BAAI/bge-small-en-v1.5) | Local ONNX-based text embeddings |
| **LLM** | Groq API (Llama 3.1 8B) | Answer generation |

---

## Key Engineering Decisions

**Why a background job queue for ingestion?**
PDF parsing, chunking, and embedding are CPU-heavy operations that can take 30–60 seconds for large documents. Doing this inline in a POST handler would block the request and risk timeout. The RQ worker decouples ingestion from the API, keeping response times fast and enabling independent scaling of the processing layer.

**Why Qdrant for vector storage?**
Qdrant is a purpose-built vector database with a clean REST/gRPC API, persistent storage, and a self-hostable Docker image. It handles nearest-neighbor search efficiently and integrates cleanly with LangChain's abstraction layer.

**Why FastEmbed instead of sentence-transformers?**
FastEmbed uses ONNX Runtime instead of PyTorch, which eliminates a ~1.5GB Docker layer (PyTorch + CUDA libraries). The `BAAI/bge-small-en-v1.5` model used here is equivalent in quality to `all-MiniLM-L6-v2` with a fraction of the infrastructure cost.

**Why Groq for LLM inference?**
Groq runs on custom LPU hardware, delivering inference speeds significantly faster than standard GPU APIs. It has a generous free tier suitable for development and demos, and requires no local model installation.

---

## Project Structure

```
├── app/
│   ├── api/
│   │   ├── main.py          # FastAPI app, router registration
│   │   ├── chat.py          # POST /chat endpoint
│   │   └── ingest.py        # POST /ingest, GET /ingest/{id}/status
│   ├── services/
│   │   ├── chat_services.py    # Chat orchestration logic
│   │   └── ingest_service.py   # PDF parsing and chunking
│   ├── clients/
│   │   ├── groq_client.py      # Groq LLM integration
│   │   └── vector_store.py     # Qdrant + FastEmbed integration
│   ├── queues/
│   │   ├── ingest_job.py       # Job enqueue logic
│   │   └── worker_tasks.py     # Worker task definition
│   ├── core/
│   │   └── config.py           # Typed settings via pydantic-settings
│   └── worker.py               # RQ worker entrypoint
├── uploads/                    # PDF upload directory (volume-mounted)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

---

## Getting Started

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- A free [Groq API key](https://console.groq.com/)

### Setup

**1. Clone the repository**

```bash
git clone https://github.com/yourusername/rag-chatbot.git
cd rag-chatbot
```

**2. Configure environment variables**

```bash
cp .env.example .env
```

Open `.env` and fill in your Groq API key:

```env
GROQ_API_KEY=your_groq_api_key_here
QDRANT_COLLECTION=rag_docs
UPLOAD_DIR=/tmp/rag_uploads
```

**3. Build and start all services**

```bash
docker compose build
docker compose up
```

All four services will start: API, Worker, Qdrant, and Valkey. The API will be available at `http://localhost:8000`.

---

## Usage

### Interactive API Docs

Open `http://localhost:8000/docs` in your browser for the full Swagger UI.

### Ingest a Document

```bash
curl -X POST http://localhost:8000/ingest \
  -F "file=@your_document.pdf"
```

Response:
```json
{
  "job_id": "abc123",
  "file": "your_document.pdf",
  "status": "queued"
}
```

### Poll Ingestion Status

```bash
curl http://localhost:8000/ingest/abc123/status
```

Response when complete:
```json
{
  "job_id": "abc123",
  "status": "finished",
  "error": null
}
```

### Ask a Question

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the main topic of the document?"}'
```

Response:
```json
{
  "answer": "Based on the document, the main topic is..."
}
```

### Health Check

```bash
curl http://localhost:8000/health
```

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Service liveness check |
| `POST` | `/ingest` | Upload a PDF for processing |
| `GET` | `/ingest/{job_id}/status` | Poll background job status |
| `POST` | `/chat` | Ask a question about ingested documents |

---

## Development

**Rebuild after code changes:**
```bash
docker compose down
docker compose build
docker compose up
```

**View live logs:**
```bash
docker compose logs -f app
docker compose logs -f worker
```

**Reset all data (wipes Qdrant collection):**
```bash
docker compose down -v
```

**Re-ingest after reset:**
Use the `/ingest` endpoint again to re-process your documents.

---

## Potential Improvements

- **Streaming responses** — Stream LLM tokens to the client as they are generated rather than waiting for the full response
- **Multi-document support** — Namespace collections per user or session
- **Reranking** — Add a cross-encoder reranker after vector retrieval to improve context quality
- **Hybrid search** — Combine vector similarity with BM25 keyword search for better retrieval on technical documents
- **Authentication** — Add API key or JWT auth to protect endpoints
- **Observability** — Integrate structured logging and a metrics endpoint for production monitoring
- **Frontend** — Chat UI with file upload, streaming display, and ingestion progress tracking

---

## License

MIT
