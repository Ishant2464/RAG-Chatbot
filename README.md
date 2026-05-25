# 🤖 RAG Chatbot — AI-Powered Document Q&A

<div align="center">

**Upload PDFs. Ask questions. Get grounded, streaming answers — with full conversation memory.**

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116-green?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black?logo=next.js)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-blue?logo=typescript)](https://www.typescriptlang.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker)](https://www.docker.com/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3-38bdf8?logo=tailwindcss)](https://tailwindcss.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

[🌐 Live Demo](https://rag-chatbot-sage.vercel.app) · [📖 API Docs](https://your-api.onrender.com/docs) · [🐛 Report Bug](https://github.com/Ishant2464/RAG-Chatbot/issues)

</div>

---

## 📖 Overview

A production-grade **Retrieval-Augmented Generation (RAG)** system built with a microservices architecture. Upload any PDF and have intelligent multi-turn conversations about its content — backed by semantic vector search, cloud embeddings, and LPU-accelerated LLM inference.

### What makes this different from a simple LLM chatbot?

| Basic LLM Chatbot | This RAG System |
|---|---|
| Hallucinated answers | Grounded answers from your actual documents |
| Single-turn, stateless | Multi-turn conversation with full context memory |
| Blocks on heavy processing | Async job queue — instant HTTP responses |
| One document at a time | Multi-document library with per-document filtering |
| Fake loading spinner | Real-time token-by-token streaming (like ChatGPT) |
| No attribution | Page-level source citations with hover previews |

---

## ✨ Features

### 🧠 Core RAG Capabilities
- **📄 Async PDF Ingestion** — Drag-and-drop upload; heavy processing (parse, chunk, embed) offloaded to RQ background worker via Redis, returning instant HTTP responses for 100+ page documents
- **🔍 Semantic Search** — Cohere `embed-english-v3.0` vectors stored in Qdrant Cloud with per-document payload indexing, enabling filtered retrieval in under 100ms
- **⚡ Streaming Responses** — Token-by-token output via Groq LPU inference (Llama 3.1 8B) + FastAPI `StreamingResponse` — no waiting for the full answer
- **💬 Multi-Turn Conversations** — Full conversation history sent with each request; the LLM maintains context across the entire session

### 🎨 Frontend Experience
- **📝 Markdown Rendering** — ReactMarkdown with syntax-highlighted code blocks for technical document Q&A
- **📑 Source Citations** — Page-level citation chips with hover tooltip previews; see exactly which page each answer came from
- **💡 Smart Follow-ups** — AI-generated suggested follow-up questions after each response, rendered as clickable chips
- **📤 Chat Export** — Download full conversations as Markdown files for offline reference

### 🏗️ Production Architecture
- **🔐 Google OAuth** — Secure authentication via Supabase Auth with per-user document isolation
- **📚 Document Library** — Multi-document sidebar with persistent document history per user; switch documents mid-conversation
- **☁️ Cloud Storage** — PDFs stored in Supabase Storage, not container filesystem; both API and Worker access via HTTPS URLs — fully stateless containers
- **🩺 Health Checks** — Worker health endpoint pings Redis; UptimeRobot monitors both services for real failures, not false positives
- **🔄 Crash Recovery** — `wait -n` in worker shell script detects any process death and exits container; Render auto-restarts instantly

---

## 🏗️ System Architecture

### Full Request Flow: Upload → Ingest → Chat

```
┌──────────────────────────────────────────────────────────────────┐
│                     VERCEL FRONTEND (Next.js 14)                 │
│                                                                  │
│  FileUpload.tsx   → Sanitize → Upload → Poll Status             │
│  ChatWindow.tsx   → Stream Tokens → Render Markdown             │
│  MessageBubble    → Citation chips + Follow-up suggestions      │
│  DocumentSidebar  → Multi-doc library + per-doc switching       │
└──────────────────────┬───────────────────────────────────────────┘
                       │ HTTPS
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│                    RENDER API SERVICE (FastAPI)                  │
│                                                                  │
│  POST /ingest                                                    │
│  ├─ Sanitize: file_[1].pdf → uuid_file_1.pdf                   │
│  ├─ Upload bytes → Supabase Storage                             │
│  └─ Enqueue RQ job with storage_url → {job_id} (instant)       │
│                                                                  │
│  GET /ingest/{job_id}/status                                     │
│  └─ Poll: queued → started → finished                           │
│                                                                  │
│  POST /chat/stream  {query, file_url, history}                  │
│  ├─ Qdrant filtered search by file_url payload (<100ms)        │
│  ├─ Build prompt with context + conversation history            │
│  └─ Groq streaming → StreamingResponse (text/plain)             │
│                                                                  │
│  POST /chat/sources      → page-level citation metadata         │
│  POST /chat/suggestions  → AI-generated follow-up questions     │
└────────────┬─────────────────────────┬───────────────────────────┘
             │                         │
             ▼                         ▼
    ┌─────────────────┐       ┌────────────────────┐
    │ Supabase Storage│       │   Groq LPU API     │
    │   (PDFs)        │       │  Llama 3.1 8B      │
    └────────┬────────┘       └────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────┐
│         RENDER WORKER SERVICE                │
│                                              │
│  Process 1: RQ Worker                       │
│  ├─ Dequeue process_doc(storage_url)        │
│  ├─ Download PDF from Supabase              │
│  ├─ PyPDF parse → 2000-char chunks          │
│  ├─ Tag: doc.metadata["file_url"]           │
│  ├─ Cohere embed-english-v3.0               │
│  └─ Batch upsert → Qdrant Cloud             │
│                                              │
│  Process 2: Uvicorn Health :8001            │
│  ├─ GET /health → ping Redis                │
│  └─ UptimeRobot monitors this               │
│                                              │
│  ⚠️  wait -n: crash → Render auto-restart   │
└────────────────┬─────────────────────────────┘
                 │
    ┌────────────┴────────────────────────┐
    │                                     │
    ▼                                     ▼
┌──────────────────────┐    ┌─────────────────────────────┐
│  Upstash Redis       │    │  Qdrant Cloud               │
│  Job queue + status  │    │  Vectors + payload metadata  │
└──────────────────────┘    │  Per-document filtered search│
                             └─────────────────────────────┘
```

---

## 💾 Technology Stack

### Backend
| Component | Technology | Why |
|---|---|---|
| **API Framework** | FastAPI + Uvicorn | Type hints, auto Swagger docs, async-native |
| **Job Queue** | RQ (Redis Queue) | Simple, Python-native, reliable async processing |
| **PDF Parsing** | PyPDF | Lightweight, no C dependencies |
| **Text Chunking** | LangChain TextSplitter | 2000-char chunks with 200-char overlap |
| **Embeddings** | Cohere `embed-english-v3.0` | Managed cloud — no local model, no Docker bloat |
| **Vector DB** | Qdrant Cloud | REST API, per-document payload filtering, persistent |
| **LLM** | Groq API (Llama 3.1 8B) | LPU hardware — fastest free-tier inference available |
| **Storage** | Supabase Storage | Stateless containers share PDFs via HTTPS URLs |
| **Auth** | Supabase Auth (Google OAuth) | Per-user document isolation |
| **Config** | Pydantic Settings | Type-safe, validated environment variables |

### Frontend
| Component | Technology | Why |
|---|---|---|
| **Framework** | Next.js 14 + TypeScript | App Router, SSR, full type safety |
| **Styling** | Tailwind CSS | Utility-first, dark theme, fully responsive |
| **Markdown** | ReactMarkdown + rehype-highlight | Rich rendering with syntax-highlighted code |
| **Streaming** | Fetch ReadableStream | Native token-by-token consumption, no WebSocket needed |
| **State** | React hooks | Simple, no Redux overhead |

### Infrastructure
| Service | Provider | Cost |
|---|---|---|
| API Server | Render | Free tier |
| Worker | Render | Free tier |
| Vector DB | Qdrant Cloud | Free tier |
| Storage + Auth | Supabase | Free tier |
| Job Queue | Upstash Redis | Free tier |
| Frontend | Vercel | Free forever |
| Monitoring | UptimeRobot | Free tier |
| LLM Inference | Groq API | Free tier |
| Embeddings | Cohere API | Usage-based |

---

## 🚀 Local Development Setup

### Prerequisites
- Python 3.11+, Docker, Docker Compose
- Node.js 18+
- Free API keys: [Groq](https://console.groq.com/keys) · [Cohere](https://dashboard.cohere.com/api-keys)

### Backend

**1. Clone and configure**
```bash
git clone https://github.com/Ishant2464/RAG-Chatbot.git
cd RAG-Chatbot
cp .env.example .env
# Fill in your API keys
```

**2. Start all services**
```bash
docker compose build
docker compose up
```

Starts: FastAPI API (`:8000`) · Qdrant (`:6333`) · Valkey/Redis (`:6379`) · RQ Worker

**3. Verify**
```bash
curl http://localhost:8000/health
# → {"status": "ok"}
```

Open [http://localhost:8000/docs](http://localhost:8000/docs) for interactive API documentation.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
# Set NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

---

## 📡 Production Deployment (Render + Vercel)

### 1. Deploy API Service on Render

```
New Web Service → GitHub repo → main branch
Start Command: bash start.sh
```

### 2. Deploy Worker Service on Render

```
New Web Service → same GitHub repo → main branch
Start Command: bash worker.sh
```

**Environment variables (set on both services):**

```env
GROQ_API_KEY=...
COHERE_API_KEY=...
QDRANT_URL=https://[cluster].qdrant.io
QDRANT_API_KEY=...
QDRANT_COLLECTION=rag_docs
REDIS_URL=rediss://...@upstash.io:6379
SUPABASE_URL=https://[project].supabase.co
SUPABASE_ANON_KEY=...
SUPABASE_BUCKET=rag-docs
UPLOAD_DIR=/tmp/rag_uploads
```

### 3. Deploy Frontend on Vercel

```
Import GitHub repo → Root Directory: frontend
Environment Variable: NEXT_PUBLIC_API_URL=https://your-api.onrender.com
```

### 4. Setup UptimeRobot (Keep-Alive + Monitoring)

Add two HTTP monitors at 5-minute intervals:
- `https://your-api.onrender.com/health`
- `https://your-worker.onrender.com/health`

Prevents Render free-tier sleep and alerts on real Redis connectivity failures.

---

## 📚 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check with Redis ping |
| `POST` | `/ingest` | Upload and queue PDF for processing |
| `GET` | `/ingest/{id}/status` | Poll background job: queued → started → finished |
| `POST` | `/chat` | Non-streaming chat (full response) |
| `POST` | `/chat/stream` | Streaming chat with conversation history |
| `POST` | `/chat/sources` | Page-level source citations for a query |
| `POST` | `/chat/suggestions` | AI-generated follow-up questions |

**Ingest a document:**
```bash
curl -X POST http://localhost:8000/ingest -F "file=@document.pdf"
# → {"job_id": "abc123", "file": "document.pdf", "status": "queued", "storage_url": "..."}
```

**Streaming chat:**
```bash
curl -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the main argument?", "file_url": "https://...", "history": []}'
# → token-by-token text stream
```

---

## 📁 Project Structure

```
rag-chatbot/
├── app/
│   ├── api/
│   │   ├── main.py              # FastAPI app + CORS middleware
│   │   ├── chat.py              # /chat, /chat/stream, /sources, /suggestions
│   │   └── ingest.py            # /ingest with filename sanitization
│   ├── services/
│   │   ├── chat_services.py     # RAG orchestration + conversation history
│   │   └── ingest_service.py    # PDF parse → chunk → embed pipeline
│   ├── clients/
│   │   ├── groq_client.py       # Groq LLM + streaming async generator
│   │   ├── vector_store.py      # Qdrant + Cohere + payload filtering
│   │   └── supabase_client.py   # Cloud storage upload/download
│   ├── queues/
│   │   ├── ingest_job.py        # RQ job enqueue
│   │   └── worker_tasks.py      # Worker task: download → parse → embed → index
│   ├── core/
│   │   └── config.py            # Pydantic Settings (all env vars, type-safe)
│   └── worker.py                # RQ worker entrypoint
├── frontend/
│   └── src/app/
│       ├── page.tsx             # Root state: auth + document selection
│       ├── layout.tsx           # Root layout + metadata
│       └── components/
│           ├── FileUpload.tsx       # Drag-and-drop + job status polling
│           ├── ChatWindow.tsx       # Streaming chat + conversation history
│           ├── MessageBubble.tsx    # Markdown + citation chips
│           ├── DocumentSidebar.tsx  # Multi-document library per user
│           └── Auth.tsx             # Google OAuth via Supabase
├── Dockerfile                   # Shared image (API + Worker)
├── docker-compose.yml           # Local dev (Qdrant + Valkey included)
├── start.sh                     # API startup script
├── worker.sh                    # Worker + health server startup
├── .env.example                 # Backend env var template
└── frontend/.env.example        # Frontend env var template
```

---

## 🎯 Key Engineering Decisions

**1. Async Job Queue — Why not process inline?**
PDF parsing + embedding 200–300 chunks takes 30–60 seconds. Synchronous processing in a POST handler causes timeouts and blocks the API. RQ decouples ingestion entirely — the API enqueues and responds in milliseconds; the worker processes independently.

**2. Cloud Storage (Supabase) — Why not local filesystem?**
The API container and Worker container have isolated filesystems. If the API saves a PDF locally, the Worker can't access it. Uploading to Supabase Storage first means both containers are fully stateless — they share data via HTTPS URLs. This is the correct distributed systems pattern.

**3. Per-Document Payload Filtering — Why not one global collection?**
Without filtering, any user's query could return chunks from any other user's document. Tagging every vector with `metadata["file_url"]` and filtering at query time enforces strict per-document, per-user isolation — critical for a multi-user system.

**4. Cohere Cloud Embeddings — Why not a local model?**
Local embedding models (sentence-transformers) pull PyTorch into Docker — that's 1.5GB+ of CUDA libraries. Cohere's API eliminates this entirely: smaller images, faster builds, faster deploys, and no GPU dependency.

**5. Streaming via ReadableStream — Why not WebSockets?**
HTTP streaming with `text/plain` + FastAPI `StreamingResponse` is simpler than WebSockets for one-directional token output, requires no persistent connection management, and works natively with the Fetch API's `ReadableStream` — zero client-side libraries needed.

**6. Separate API + Worker Render Services — Why not combined?**
Render's free tier provides 512MB RAM per service. FastAPI uses ~100MB; the Worker embedding a large PDF peaks at ~300MB. Combined, they breach the limit. Separate services each get 512MB independently, and if the Worker crashes it doesn't take the API down with it.

---

## 📊 Performance

| Operation | Typical Time |
|---|---|
| PDF upload | ~1–2 sec |
| Document processing (10 pages, ~80 chunks) | ~15–20 sec |
| Document processing (100 pages, ~266 chunks) | ~45–60 sec |
| Qdrant filtered semantic search | ~80–120 ms |
| First token (Groq LPU) | ~300–500 ms |
| Full streaming response | ~1–3 sec |

---

## 🛠️ Useful Commands

```bash
# Start local dev stack
docker compose up --build

# View live logs
docker compose logs -f
docker compose logs -f app
docker compose logs -f worker

# Reset all data (wipes Qdrant collection)
docker compose down -v

# Quick API tests
curl http://localhost:8000/health
curl -X POST http://localhost:8000/ingest -F "file=@test.pdf"

# Frontend
cd frontend && npm run dev
cd frontend && npm run build
```

---

## 🌍 Environment Variables

| Variable | Description | Source |
|---|---|---|
| `GROQ_API_KEY` | Groq LLM API key | [console.groq.com](https://console.groq.com) |
| `COHERE_API_KEY` | Cohere embeddings key | [dashboard.cohere.com](https://dashboard.cohere.com) |
| `QDRANT_URL` | Qdrant server URL | [cloud.qdrant.io](https://cloud.qdrant.io) or `http://localhost:6333` |
| `QDRANT_API_KEY` | Qdrant API key (cloud only) | [cloud.qdrant.io](https://cloud.qdrant.io) |
| `QDRANT_COLLECTION` | Collection name | Default: `rag_docs` |
| `REDIS_URL` | Redis connection URL | [upstash.com](https://upstash.com) or `redis://localhost:6379` |
| `SUPABASE_URL` | Supabase project URL | Supabase dashboard |
| `SUPABASE_ANON_KEY` | Supabase anonymous key | Supabase dashboard |
| `SUPABASE_BUCKET` | Storage bucket name | Default: `rag-docs` |
| `UPLOAD_DIR` | Temp upload path | Default: `/tmp/rag_uploads` |
| `NEXT_PUBLIC_API_URL` | Backend URL for frontend | Your Render API URL |
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase URL (frontend) | Supabase dashboard |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase key (frontend) | Supabase dashboard |

---

## 📝 License

MIT

---

<div align="center">
  Built with FastAPI · Groq · Cohere · Qdrant · LangChain · Supabase · Next.js · Render · Vercel
</div>