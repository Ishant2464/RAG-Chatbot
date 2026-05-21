# 🚀 Scalable RAG Chatbot

> A **production-grade Retrieval-Augmented Generation (RAG) system** that enables intelligent document Q&A with background job processing, distributed services, and real-world engineering patterns.

Upload PDF documents, ask natural language questions, and get grounded answers powered by semantic search + LLM reasoning. Built for **scalability, reliability, and enterprise-grade architecture**.

---

## ✨ Features

### Core Capabilities
- ✅ **Document Ingestion** — Upload PDFs, automatically parse, chunk, embed, and index
- ✅ **Semantic Search** — Cohere embeddings find relevant document sections
- ✅ **LLM-Powered Answers** — Groq API (llama-3.1) generates grounded responses
- ✅ **Multi-Document Support** — Each upload gets a unique file_url metadata tag for isolated retrieval
- ✅ **Async Processing** — Background job queue prevents blocking; handle 30–60 second PDFs instantly
- ✅ **Job Status Polling** — Track document processing in real-time via REST API

### Production Features
- ✅ **Cloud Storage** — PDFs stored in Supabase Storage, not container filesystem (distributed architecture)
- ✅ **Filename Sanitization** — Automatic cleanup of special characters (brackets, spaces, etc.)
- ✅ **Health Checks** — API and Worker services expose `/health` endpoints with Redis verification
- ✅ **UptimeRobot Integration** — Automatic monitoring prevents free-tier service spindown
- ✅ **CORS Configured** — Works seamlessly with Vercel frontend
- ✅ **Process Monitoring** — Worker service auto-restarts on crash; `wait -n` detects failures instantly
- ✅ **Type Safety** — Full TypeScript frontend, Pydantic-validated backend

---

## 🏗️ System Architecture

### Component Interaction: Upload → Chat Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                     VERCEL FRONTEND (Next.js)                    │
│  FileUpload.tsx → Sanitize → Upload → Poll → ChatWindow.tsx     │
└──────────────────────┬──────────────────────────────────────────┘
                       │ HTTPS
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│                    RENDER API SERVICE                            │
│         (FastAPI running start.sh)                              │
│                                                                  │
│  POST /ingest                                                   │
│  ├─ Receive PDF bytes + filename                              │
│  ├─ Sanitize: file_[1].pdf → uuid_file_1.pdf                 │
│  ├─ Upload to Supabase Storage                                 │
│  └─ Enqueue RQ job with storage_url (not local path!)          │
│                                                                  │
│  GET /ingest/{job_id}/status                                   │
│  ├─ Frontend polls every 1 sec                                 │
│  └─ status: queued → started → finished                        │
│                                                                  │
│  POST /chat {query, file_url}                                  │
│  ├─ Search Qdrant FILTERED by file_url                        │
│  ├─ Only retrieve chunks from specific document               │
│  ├─ Call Groq API                                             │
│  └─ Stream response back                                       │
└───────────┬─────────────────────────┬──────────────┬───────────┘
            │                         │              │
            ▼                         ▼              ▼
       ┌─────────────┐        ┌──────────────┐   ┌─────────────┐
       │ Supabase    │        │ Qdrant Cloud │   │  Groq API   │
       │ Storage     │        │ (Vectors +   │   │             │
       │ (PDFs)      │        │  Metadata)   │   │ llama-3.1   │
       └─────────────┘        └──────────────┘   └─────────────┘
            ▲                         ▲
            │                         │
            └────────────────┬────────┘
                             │
    ┌────────────────────────▼──────────────────────┐
    │      RENDER WORKER SERVICE                   │
    │   (worker.sh: RQ Worker + Uvicorn Health)   │
    │                                              │
    │  Process 1: RQ Worker                       │
    │  ├─ Dequeue process_doc(storage_url)       │
    │  ├─ Download PDF from Supabase             │
    │  ├─ PyPDF parse                            │
    │  ├─ Add metadata: doc.metadata["file_url"] │
    │  ├─ Split into 2000-char chunks           │
    │  ├─ Cohere embeddings → vectors           │
    │  └─ Store in Qdrant                        │
    │                                              │
    │  Process 2: Uvicorn Health Server :8000    │
    │  ├─ GET /health                            │
    │  ├─ Verify Redis connection                │
    │  └─ UptimeRobot monitors this              │
    │                                              │
    │  ⚠️ If either crashes:                      │
    │     wait -n detects → exit container        │
    │     → Render auto-restart                   │
    └───────────┬────────────────────────────────┘
                │ Redis connection
                │
    ┌───────────▼────────────────────┐
    │  Upstash Redis (Cloud)         │
    │  - Job queue                   │
    │  - Job status                  │
    │  - Connection pooling          │
    └────────────────────────────────┘
```

---

## 💾 Technology Stack

### Backend
| Component | Technology | Why? |
|-----------|-----------|------|
| **API Framework** | FastAPI + Uvicorn | Type hints, auto docs, async-native |
| **Job Queue** | RQ (Redis Queue) | Simple, Python-native, reliable |
| **PDF Parsing** | PyPDF | Lightweight, no C deps |
| **Text Chunking** | LangChain TextSplitter | Context-aware splitting |
| **Embeddings** | Cohere `embed-english-v3.0` | Managed cloud embeddings; no local model download |
| **Vector DB** | Qdrant | REST API, metadata filtering, cloud-hosted |
| **LLM** | Groq API (llama-3.1-8b) | Fast, free tier, no local model |
| **Config** | Pydantic Settings | Type-safe environment variables |
| **Storage** | Supabase Storage | Cheap, easy RLS policies, public URLs |

### Frontend
| Component | Technology | Why? |
|-----------|-----------|------|
| **Framework** | Next.js 14 (React) | SSR, built-in optimization, TypeScript |
| **Styling** | Tailwind CSS | Utility-first, responsive |
| **State** | React hooks | Simple, no Redux needed |
| **HTTP** | Fetch API | Native, no external deps |
| **Deployment** | Vercel | Auto-deploy, environment vars |

### Infrastructure
| Component | Service | Cost |
|-----------|---------|------|
| **API Server** | Render | $7/mo |
| **Worker** | Render | $7/mo |
| **Vector DB** | Qdrant Cloud | Free tier |
| **Storage** | Supabase | Free tier |
| **Job Queue** | Upstash Redis | Free tier |
| **Frontend** | Vercel | Free tier |
| **Monitoring** | UptimeRobot | Free tier |
| **LLM** | Groq API | Free tier |
| **Embeddings** | Cohere API | Usage-based |
| **Total** | | ~$14/mo |

---

## 🚀 Local Development Setup

### Prerequisites
- Python 3.11+, Docker, Docker Compose
- Node.js 18+
- Free Groq API key: https://console.groq.com/keys
- Cohere API key: https://dashboard.cohere.com/api-keys

### Backend

**1. Clone & configure**
```bash
git clone https://github.com/yourusername/rag-chatbot.git
cd rag-chatbot
cp .env.example .env
```

**2. Edit `.env`**
```env
GROQ_API_KEY=gsk_...
COHERE_API_KEY=...
QDRANT_URL=http://localhost:6333
REDIS_URL=redis://localhost:6379
```

**3. Start services**
```bash
docker compose build
docker compose up
```

Services: API (8000), Qdrant (6333), Valkey (6379)

### Frontend

**1. Install & configure**
```bash
cd frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

**2. Run dev server**
```bash
npm run dev
```

Frontend: http://localhost:3000

---

## 📡 Production Deployment (Render + Vercel)

### 1. Deploy API Service

```
Render Dashboard → Create Web Service
├─ GitHub repo
├─ Branch: main
├─ Build: (blank)
├─ Start: (blank, uses Dockerfile CMD)
├─ Environment Variables:
│  ├─ GROQ_API_KEY=...
│  ├─ COHERE_API_KEY=...
│  ├─ QDRANT_URL=https://[cluster].qdrant.io
│  ├─ QDRANT_API_KEY=...
│  ├─ REDIS_URL=rediss://...@upstash.io:6379
│  ├─ SUPABASE_URL=https://[project].supabase.co
│  ├─ SUPABASE_ANON_KEY=...
│  └─ SUPABASE_BUCKET=rag-docs
└─ Create Web Service
```

### 2. Deploy Worker Service

```
Same as above but:
├─ Name: rag-chatbot-worker
├─ Start: bash worker.sh  ← CRITICAL!
└─ Same env vars
```

### 3. Configure Supabase

```
Supabase Dashboard
├─ Storage → rag-docs bucket
├─ Policies → New Policy:
│  ├─ Name: Allow uploads
│  ├─ Operations: INSERT ✓, SELECT ✓
│  ├─ Target Roles: anon
│  └─ WITH CHECK: true
```

### 4. Setup UptimeRobot

```
UptimeRobot → Add Monitor
├─ Type: HTTP(s)
├─ URL: https://rag-chatbot-[id].onrender.com/health
├─ Interval: 5 minutes
├─ Add another for worker:
│  └─ URL: https://rag-chatbot-worker-[id].onrender.com/health
```

### 5. Deploy Frontend

```
Vercel Dashboard → Import
├─ Frontend folder
├─ Environment Variables:
│  └─ NEXT_PUBLIC_API_URL=https://rag-chatbot-[id].onrender.com
└─ Deploy
```

---

## 📚 API Reference

### POST /ingest
Upload and queue a PDF for processing.

```bash
curl -X POST http://localhost:8000/ingest \
  -F "file=@document.pdf"
```

**Response:**
```json
{
  "job_id": "b9ab8c5f-1234-5678",
  "file": "document.pdf",
  "status": "queued",
  "storage_url": "https://yafiakrb...rag-docs/3a2f1c2e_document.pdf"
}
```

### GET /ingest/{job_id}/status
Poll job completion status.

```bash
curl http://localhost:8000/ingest/b9ab8c5f-1234-5678/status
```

**Response:** `{status: "queued|started|finished|failed"}`

### POST /chat
Ask a question (requires file_url).

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is this about?",
    "file_url": "https://..."
  }'
```

**Response:** `{answer: "Based on the document..."}`

### GET /health
Health check (for UptimeRobot).

```bash
curl http://localhost:8000/health
```

---

## 📁 Project Structure

```
rag-chatbot/
├── app/
│   ├── api/
│   │   ├── main.py           # FastAPI + CORS
│   │   ├── chat.py           # POST /chat endpoint
│   │   └── ingest.py         # POST /ingest (with sanitization)
│   ├── services/
│   │   ├── chat_services.py  # Orchestration logic
│   │   └── ingest_service.py # Parse + chunk + embed
│   ├── clients/
│   │   ├── groq_client.py    # LLM integration
│   │   ├── vector_store.py   # Qdrant + metadata filtering
│   │   └── supabase_client.py # Cloud storage upload
│   ├── queues/
│   │   ├── ingest_job.py     # RQ job enqueue
│   │   └── worker_tasks.py   # Worker task def
│   ├── core/
│   │   └── config.py         # Pydantic env vars
│   └── worker.py             # RQ worker entrypoint
├── frontend/
│   ├── src/app/
│   │   ├── page.tsx          # Main page (state mgmt)
│   │   └── components/
│   │       ├── FileUpload.tsx    # Upload + polling
│   │       └── ChatWindow.tsx    # Chat UI
│   └── tailwind.config.js
├── Dockerfile                # Shared by API + Worker
├── docker-compose.yml        # Local dev
├── start.sh                  # API startup (Uvicorn)
├── worker.sh                 # Worker startup (RQ + Health)
└── README.md                 # This file
```

---

## 🎯 Key Engineering Decisions

### 1. Async Job Queue
**Problem:** PDF processing takes 30–60s; can't do synchronously in HTTP request.
**Solution:** RQ worker dequeues asynchronously. API returns job_id immediately.
**Result:** Instant user feedback; processing independent.

### 2. Cloud Storage (Supabase)
**Problem:** Containers have isolated filesystems. API saves locally; Worker can't access.
**Solution:** API uploads to Supabase; Worker downloads via HTTPS URL.
**Result:** Both containers stateless; no filesystem sync issues.

### 3. File URL Metadata Tagging
**Problem:** All documents mixed in Qdrant. User A gets answers from User B's docs.
**Solution:** Tag all chunks with `metadata["file_url"]`. Chat filters by file_url.
**Result:** Each document searchable independently; multi-user safe.

### 4. 2000-Char Chunks
**Problem:** Too small = fragmented; too large = LLM uses wrong sections.
**Solution:** 2000-char chunks with 200-char overlap.
**Result:** Good semantic context + precise retrieval.

### 5. Cloud Embeddings (Cohere)
**Problem:** Local embedding models increase image size and deployment complexity.
**Solution:** Use Cohere `embed-english-v3.0` through the cloud API.
**Result:** Smaller containers, simpler builds, and managed embedding quality.

### 6. Separate API + Worker Services
**Problem:** 512MB RAM limit; API + Worker together can exceed it.
**Solution:** Run as two separate Render services, each gets 512MB.
**Result:** Stable system; if Worker crashes, API keeps serving /health.

### 7. Process Monitoring in Worker
**Problem:** Dummy HTTP servers look healthy but might not be working.
**Solution:** Health endpoint pings Redis; only 200 if connection succeeds.
**Result:** UptimeRobot detects real failures, not false positives.

---

## 🎓 Portfolio Value

This project demonstrates:
- ✅ **Async Architecture** — Job queues, background processing, polling
- ✅ **Distributed Systems** — Stateless services, cloud storage, metadata isolation
- ✅ **Real-World Constraints** — Free tier optimization, RAM budgets, cold starts
- ✅ **DevOps** — Docker, environment configs, health checks, monitoring
- ✅ **Full-Stack** — React frontend, FastAPI backend, cloud infrastructure
- ✅ **Type Safety** — TypeScript + Pydantic
- ✅ **RAG Internals** — Embeddings, vector search, LLM prompting

Perfect for **internships, ML engineering interviews, portfolio projects**.

---

## 📊 Performance

| Operation | Time |
|-----------|------|
| Upload 10-page PDF | ~2 sec |
| Process 10-page PDF | ~15–20 sec |
| Semantic search | ~200 ms |
| LLM inference | ~1–2 sec |
| End-to-end chat | ~2–3 sec |

---

## 🛠️ Useful Commands

```bash
# Local dev
docker compose up
docker compose logs -f api
docker compose logs -f worker

# Test API
curl -X POST http://localhost:8000/ingest -F "file=@test.pdf"
curl http://localhost:8000/health

# Frontend
cd frontend && npm run dev
npm run build
```

---

## 📝 License

MIT

---

## 🙏 Credits

Built with **FastAPI**, **Groq**, **Cohere**, **Qdrant**, **LangChain**, **Supabase**, **Render**, **Vercel**.
