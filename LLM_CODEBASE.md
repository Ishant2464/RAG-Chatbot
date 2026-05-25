# RAG Chatbot — Full Codebase Export for LLM Context

> Auto-generated snapshot. Excludes: node_modules, .next, __pycache__, venv, package-lock.json, .env secrets, uploads, build artifacts.

## How to use
Paste this entire file into an LLM when asking for code review, debugging, or modifications.

## Architecture summary
- **Backend** (`app/`): FastAPI — ingest PDFs to Supabase Storage, RQ worker embeds into Qdrant, Groq LLM for chat
- **Frontend** (`frontend/`): Next.js 14 — Google OAuth via Supabase, streaming chat, document sidebar
- **Infra**: Docker Compose (local), Render (API + Worker), Vercel (frontend)

## File index
- `README.md`
- `SETUP.md`
- `.env.example`
- `.gitignore`
- `app/__init__.py`
- `app/api/__init__.py`
- `app/api/chat.py`
- `app/api/ingest.py`
- `app/api/main.py`
- `app/api/sources.py`
- `app/api/suggestions.py`
- `app/clients/__init__.py`
- `app/clients/groq_client.py`
- `app/clients/supabase_client.py`
- `app/clients/vector_store.py`
- `app/core/__init__.py`
- `app/core/config.py`
- `app/queues/__init__.py`
- `app/queues/ingest_job.py`
- `app/queues/worker_tasks.py`
- `app/services/__init__.py`
- `app/services/chat_services.py`
- `app/services/ingest_service.py`
- `app/worker.py`
- `app/worker_health.py`
- `docker-compose.prod.yml`
- `docker-compose.yml`
- `Dockerfile`
- `frontend/.env.example`
- `frontend/next.config.js`
- `frontend/package.json`
- `frontend/postcss.config.js`
- `frontend/src/app/components/AuthProvider.tsx`
- `frontend/src/app/components/ChatWindow.tsx`
- `frontend/src/app/components/DocumentSidebar.tsx`
- `frontend/src/app/components/FileUpload.tsx`
- `frontend/src/app/components/LoginScreen.tsx`
- `frontend/src/app/components/MessageBubble.tsx`
- `frontend/src/app/globals.css`
- `frontend/src/app/layout.tsx`
- `frontend/src/app/page.tsx`
- `frontend/src/lib/supabase.ts`
- `frontend/tailwind.config.js`
- `frontend/tsconfig.json`
- `INTERVIEW_NOTES.md`
- `requirements.txt`
- `start.sh`
- `worker.sh`

---

## FILE: `README.md`

```markdown
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
```

---

## FILE: `SETUP.md`

```markdown
# 🚀 Complete Setup & Deployment Guide — RAG Chatbot

This guide covers everything from zero to a fully deployed, production-running RAG chatbot. Follow phases in order. Do not skip a phase — each one depends on the previous.

---

## Prerequisites

Before starting, install these on your machine:

- **Docker Desktop** — [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop) — must be running in system tray
- **Node.js 18+** — [nodejs.org](https://nodejs.org) — verify with `node --version`
- **Git** — [git-scm.com](https://git-scm.com)
- **VS Code** (recommended) — [code.visualstudio.com](https://code.visualstudio.com)

Verify Docker is working:
```bash
docker --version
docker compose version
```

Both should print version numbers. If Docker Desktop isn't running, start it before proceeding.

---

## Phase 1: Groq API Key (LLM Inference)

Groq provides free LLM inference on custom LPU hardware — significantly faster than standard GPU APIs.

**Step 1.** Go to [console.groq.com](https://console.groq.com) → Sign up with Google or email

**Step 2.** In the left sidebar → click **API Keys** → click **Create API Key**

**Step 3.** Give it a name (e.g., `rag-chatbot-local`) → click **Submit**

**Step 4.** Copy the key immediately — it starts with `gsk_` — it is only shown once. Save it somewhere safe.

**Step 5.** Keep this tab open. You will paste this into `.env` later.

> Free tier limits: ~14,400 requests/day, ~30 requests/minute for Llama 3.1 8B. More than enough for development and demos.

---

## Phase 2: Cohere API Key (Embeddings)

Cohere provides the embedding model that converts your document chunks into vectors.

**Step 6.** Go to [dashboard.cohere.com](https://dashboard.cohere.com) → Sign up

**Step 7.** In the left sidebar → click **API Keys** → you will see a default trial key already created

**Step 8.** Copy the trial key — it starts with a long alphanumeric string

**Step 9.** Save it. You will paste this into `.env` later.

> The trial key works indefinitely for low-volume usage. No credit card needed.

---

## Phase 3: Qdrant Cloud (Vector Database)

Qdrant Cloud hosts your document embeddings and enables sub-100ms semantic search.

**Step 10.** Go to [cloud.qdrant.io](https://cloud.qdrant.io) → Sign up with Google or email

**Step 11.** After login → click **Create Cluster**

**Step 12.** Fill in:
- Name: `rag-chatbot`
- Cloud Provider: AWS (default)
- Region: pick the closest one to you (e.g., `us-east-1`)
- Tier: **Free** (1GB, enough for demos)

**Step 13.** Click **Create** → wait ~30 seconds for the cluster to provision

**Step 14.** Once the cluster shows **Running**:
- Click on the cluster name
- Copy the **Cluster URL** — looks like `https://xxxx-xxxx-xxxx.aws.cloud.qdrant.io`

**Step 15.** In the cluster page → click **API Keys** tab → click **Create API Key**
- Give it a name → click **Create**
- Copy the API key immediately — shown only once

**Step 16.** Save both the Cluster URL and API Key.

---

## Phase 4: Upstash Redis (Job Queue)

Upstash provides a serverless Redis instance used by the RQ job queue to pass ingestion jobs from the API to the Worker.

**Step 17.** Go to [upstash.com](https://upstash.com) → Sign up with GitHub or Google

**Step 18.** Click **Create Database**

**Step 19.** Fill in:
- Name: `rag-chatbot-queue`
- Type: **Regional**
- Region: pick closest to you
- TLS: **Enabled** (keep on)

**Step 20.** Click **Create**

**Step 21.** On the database page → scroll down to **REST API** section → find the **UPSTASH_REDIS_REST_URL** — but you actually need the Redis connection URL, not the REST URL

**Step 22.** Scroll to the **Connect** section → click **Redis CLI** tab → copy the connection string that looks like:
```
rediss://default:XXXXXXXXX@your-db.upstash.io:6379
```
This is your `REDIS_URL`. Save it.

> The `rediss://` (with double s) means TLS-encrypted Redis. Required for Upstash cloud connections.

---

## Phase 5: Supabase (Storage + Authentication)

Supabase handles two things: storing the uploaded PDFs in cloud storage, and Google OAuth for user authentication.

**Step 23.** Go to [supabase.com](https://supabase.com) → Sign up with GitHub

**Step 24.** Click **New Project**
- Name: `rag-chatbot`
- Database Password: generate a strong one and save it
- Region: closest to you
- Click **Create new project** → wait ~2 minutes

**Step 25.** Once the project is ready → go to **Settings** (gear icon, left sidebar) → **API**
- Copy **Project URL** → this is your `SUPABASE_URL`
- Copy **anon public** key → this is your `SUPABASE_ANON_KEY`

**Step 26.** Create the storage bucket:
- In left sidebar → **Storage** → **New Bucket**
- Bucket name: `rag-docs`
- **Public bucket**: toggle ON (required so the Worker can download PDFs via HTTPS URL)
- Click **Save**

**Step 27.** Set up storage policy (allow uploads):
- In Storage → click your `rag-docs` bucket → **Policies** tab
- Click **New Policy** → **For full customization**
- Policy name: `Allow public access`
- Allowed operations: check **SELECT**, **INSERT**
- Target roles: `anon`
- USING expression: `true`
- WITH CHECK expression: `true`
- Click **Review** → **Save policy**

**Step 28.** Enable Google OAuth:
- In left sidebar → **Authentication** → **Providers**
- Find **Google** → toggle **Enable**
- You will need a Google OAuth Client ID and Secret. To get these:
  - Go to [console.cloud.google.com](https://console.cloud.google.com)
  - Create a new project (or use existing)
  - Go to **APIs & Services** → **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
  - Application type: **Web application**
  - Authorized redirect URIs: add `https://[your-supabase-project-ref].supabase.co/auth/v1/callback`
    (find your project ref in Supabase Settings → General)
  - Click **Create** → copy **Client ID** and **Client Secret**
- Back in Supabase → paste your Google Client ID and Client Secret → **Save**

**Step 29.** Add your local URL to Supabase Auth:
- In Authentication → **URL Configuration**
- Site URL: `http://localhost:3000`
- Additional redirect URLs: add `http://localhost:3000/auth/callback`
- Click **Save**

---

## Phase 6: Local Environment Setup

Now that all external services are ready, configure your local environment.

**Step 30.** Clone the repository:
```bash
git clone https://github.com/Ishant2464/RAG-Chatbot.git
cd RAG-Chatbot
```

**Step 31.** Create your backend `.env` file:
```bash
cp .env.example .env
```

**Step 32.** Open `.env` in VS Code and fill in every value:
```env
# LLM
GROQ_API_KEY=gsk_your_key_from_phase_1

# Embeddings
COHERE_API_KEY=your_key_from_phase_2

# Vector Database
QDRANT_URL=https://xxxx-xxxx.aws.cloud.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key_from_phase_3
QDRANT_COLLECTION=rag_docs

# Job Queue
REDIS_URL=rediss://default:xxxxx@your-db.upstash.io:6379

# Storage & Auth
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_ANON_KEY=your_anon_key_from_phase_5
SUPABASE_BUCKET=rag-docs

# Upload temp directory
UPLOAD_DIR=/tmp/rag_uploads
```

**Step 33.** Create the frontend environment file:
```bash
cd frontend
cp .env.example .env.local
```

**Step 34.** Open `frontend/.env.local` and fill in:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://xxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key_from_phase_5
```

**Step 35.** Go back to the project root:
```bash
cd ..
```

---

## Phase 7: Run the Backend Locally

**Step 36.** Build the Docker images (first build takes 3–5 minutes, subsequent builds use cache):
```bash
docker compose build
```

Watch the output. You should see packages installing cleanly. There should be no errors. If you see a red error line, check that `.env` is filled correctly and Docker Desktop is running.

**Step 37.** Start all services:
```bash
docker compose up
```

You should see 4 services start:
```
vector-db-1  | Qdrant HTTP listening on 6333
valkey-1     | Ready to accept connections tcp
app-1        | Application startup complete.
worker-1     | Listening on default...
```

Wait until all 4 show their ready messages before proceeding.

**Step 38.** In a second terminal, verify everything is healthy:
```bash
curl http://localhost:8000/health
```
Expected: `{"status": "ok"}`

**Step 39.** Open the interactive API docs in Chrome:
```
http://localhost:8000/docs
```
You should see all endpoints listed: `/ingest`, `/ingest/{id}/status`, `/chat`, `/chat/stream`, `/chat/sources`, `/chat/suggestions`, `/health`.

---

## Phase 8: Run the Frontend Locally

**Step 40.** Open a new terminal tab (keep Docker running in the previous one):
```bash
cd frontend
npm install
```

This takes 1–2 minutes on first run.

**Step 41.** Start the Next.js dev server:
```bash
npm run dev
```

Expected output:
```
▲ Next.js 14.x.x
- Local: http://localhost:3000
✓ Ready in 2.1s
```

**Step 42.** Open Chrome and go to `http://localhost:3000`

---

## Phase 9: Test Everything Locally

Work through this checklist in order. If any step fails, stop and fix it before continuing.

**Step 43.** Test authentication:
- On the homepage → click **Sign in with Google**
- Complete Google OAuth flow
- You should be redirected back to the app and see the main UI
- ✅ Auth is working

**Step 44.** Test PDF upload:
- Find any PDF on your computer (use a short one, 5–20 pages, for faster testing)
- In the app → drag and drop the PDF onto the upload area (or click to browse)
- You should see the status change: `Uploading...` → `Processing document...`
- In your Docker terminal you should see:
  ```
  worker-1 | [Ingest] Loading document: ...
  worker-1 | [Ingest] Loaded X pages
  worker-1 | [Ingest] Split into X chunks
  worker-1 | [Ingest] Indexed X chunks into Qdrant
  ```
- Status should reach `Document ready`
- ✅ Ingestion pipeline is working

**Step 45.** Test chat with streaming:
- Once document is ready → type a question about the document
- You should see tokens appear one by one as the answer streams in
- The answer should be grounded in the document content, not generic
- ✅ Retrieval + streaming LLM is working

**Step 46.** Test source citations:
- After an answer appears → citation chips should show page numbers
- Hover over a chip → tooltip preview should appear
- ✅ Citations are working

**Step 47.** Test follow-up suggestions:
- Below the answer → clickable suggested questions should appear
- Click one → it should populate the input and send
- ✅ Suggestions are working

**Step 48.** Test multi-document library:
- Upload a second PDF
- In the sidebar → both documents should appear
- Switch between them → chat should change context to the selected document
- ✅ Multi-document library is working

**Step 49.** Test chat export:
- Have a multi-turn conversation
- Click the export button → a `.md` file should download
- Open it → conversation should be formatted correctly
- ✅ Chat export is working

**Step 50.** Test conversation memory:
- Ask a question → get an answer
- Ask a follow-up that references the previous answer (e.g., "Can you elaborate on that?")
- The LLM should respond with context from the previous turn
- ✅ Multi-turn conversation memory is working

All 8 checks pass? Your local setup is complete and fully functional.

---

## Phase 10: Deploy Backend on Render

**Step 51.** Push your code to GitHub:
```bash
git add .
git commit -m "production-ready RAG chatbot"
git push origin main
```

Make sure `.env` and `.env.local` are NOT in the commit. Check with:
```bash
git status
```
Neither file should appear. If they do, your `.gitignore` is not set up correctly — add them and commit the `.gitignore` first.

**Step 52.** Go to [render.com](https://render.com) → Sign up with GitHub

**Step 53.** Deploy the API service:
- Click **New** → **Web Service**
- Connect your GitHub account → select your `RAG-Chatbot` repository
- Branch: `main`
- Name: `rag-chatbot-api`
- Runtime: **Docker**
- Start Command: `bash start.sh`
- Instance Type: **Free**
- Click **Create Web Service**

**Step 54.** Before Render finishes the first deploy, add all environment variables:
- In the service page → **Environment** tab → **Add Environment Variable** — add each one:

```
GROQ_API_KEY          = gsk_your_key
COHERE_API_KEY        = your_key
QDRANT_URL            = https://xxxx.aws.cloud.qdrant.io
QDRANT_API_KEY        = your_qdrant_key
QDRANT_COLLECTION     = rag_docs
REDIS_URL             = rediss://default:xxxxx@upstash.io:6379
SUPABASE_URL          = https://xxxx.supabase.co
SUPABASE_ANON_KEY     = your_anon_key
SUPABASE_BUCKET       = rag-docs
UPLOAD_DIR            = /tmp/rag_uploads
```

**Step 55.** Click **Save Changes** → Render will trigger a new deploy

**Step 56.** Watch the deploy logs. A successful deploy ends with:
```
Application startup complete.
```
Copy your API URL — looks like `https://rag-chatbot-api-xxxx.onrender.com`

**Step 57.** Deploy the Worker service:
- Click **New** → **Web Service** again
- Same GitHub repo → same branch
- Name: `rag-chatbot-worker`
- Runtime: **Docker**
- Start Command: `bash worker.sh`
- Instance Type: **Free**
- Add the **exact same environment variables** as Step 54
- Click **Create Web Service**

**Step 58.** Wait for the Worker deploy to finish. Copy the Worker URL — looks like `https://rag-chatbot-worker-xxxx.onrender.com`

**Step 59.** Test both health endpoints:
```bash
curl https://rag-chatbot-api-xxxx.onrender.com/health
curl https://rag-chatbot-worker-xxxx.onrender.com/health
```
Both should return `{"status": "ok"}`. If the worker health check also pings Redis, it confirms the Redis connection is live too.

---

## Phase 11: Deploy Frontend on Vercel

**Step 60.** Go to [vercel.com](https://vercel.com) → Sign up with GitHub

**Step 61.** Click **Add New Project** → import your `RAG-Chatbot` repository

**Step 62.** Configure the project:
- **Root Directory**: click **Edit** → type `frontend` → click **Continue**
- Framework Preset: Next.js (auto-detected)

**Step 63.** Add environment variables (before clicking Deploy):
- Click **Environment Variables** → add:

```
NEXT_PUBLIC_API_URL              = https://rag-chatbot-api-xxxx.onrender.com
NEXT_PUBLIC_SUPABASE_URL         = https://xxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY    = your_anon_key
```

**Step 64.** Click **Deploy** → wait 2–3 minutes

**Step 65.** Once deployed, copy your Vercel URL — looks like `https://rag-chatbot-sage.vercel.app`

**Step 66.** Update Supabase Auth to allow your production URL:
- In Supabase → **Authentication** → **URL Configuration**
- Add to **Additional Redirect URLs**:
  ```
  https://rag-chatbot-sage.vercel.app
  https://rag-chatbot-sage.vercel.app/auth/callback
  ```
- Update **Site URL** to your Vercel URL
- Click **Save**

**Step 67.** Update CORS in your backend:
- In `app/api/main.py` → find the `allow_origins` list → add your Vercel URL:
  ```python
  allow_origins=[
      "http://localhost:3000",
      "https://*.vercel.app",
      "https://rag-chatbot-sage.vercel.app",  # your exact URL
  ]
  ```
- Push to GitHub → Render will auto-redeploy the API

---

## Phase 12: UptimeRobot (Keep-Alive + Monitoring)

Render's free tier sleeps after 15 minutes of inactivity. UptimeRobot prevents this by pinging every 5 minutes — for free.

**Step 68.** Go to [uptimerobot.com](https://uptimerobot.com) → Sign up free

**Step 69.** Click **Add New Monitor** — set up monitor for the API:
- Monitor Type: **HTTP(s)**
- Friendly Name: `RAG Chatbot API`
- URL: `https://rag-chatbot-api-xxxx.onrender.com/health`
- Monitoring Interval: **5 minutes**
- Click **Create Monitor**

**Step 70.** Click **Add New Monitor** again — set up monitor for the Worker:
- Monitor Type: **HTTP(s)**
- Friendly Name: `RAG Chatbot Worker`
- URL: `https://rag-chatbot-worker-xxxx.onrender.com/health`
- Monitoring Interval: **5 minutes**
- Click **Create Monitor**

Both monitors will show green after the first successful ping. You will receive email alerts if either service goes down.

> Why the Worker has a health endpoint: a dummy server that always returns 200 isn't useful. Your Worker's health endpoint pings Redis and only returns 200 if the connection succeeds — so UptimeRobot catches real queue failures, not just process-alive checks.

---

## Phase 13: Final Production Verification

Go through this checklist on your **production Vercel URL**, not localhost.

- [ ] Open `https://your-app.vercel.app` → page loads cleanly, no console errors
- [ ] Click **Sign in with Google** → OAuth flow completes → redirected back to app
- [ ] Drag and drop a PDF → status progresses from `Uploading` → `Processing` → `Document ready`
- [ ] In Docker logs (or Render worker logs): see `[Ingest] Indexed X chunks into Qdrant`
- [ ] Ask a question about the uploaded document → tokens stream in one by one
- [ ] Answer is grounded in document content (not generic)
- [ ] Source citation chips appear below the answer
- [ ] Hover over a citation chip → tooltip preview shows
- [ ] Click a follow-up suggestion → it sends and gets a streaming response
- [ ] Upload a second document → both appear in the sidebar
- [ ] Switch documents → chat context changes correctly
- [ ] Have a 3-turn conversation → later turns reference earlier answers correctly
- [ ] Click export → `.md` file downloads with full conversation
- [ ] Check UptimeRobot dashboard → both monitors show green
- [ ] `curl https://your-api.onrender.com/health` → `{"status": "ok"}`

All green? Your project is fully live and production-ready.

---

## Common Errors and Fixes

**Docker build fails with `pip install` error**
```bash
docker compose down
docker compose build --no-cache
```
If it still fails, check your internet connection — some packages are large.

**`curl http://localhost:8000/health` returns "Connection refused"**
The app container hasn't finished starting. Wait 10 more seconds and retry. Check `docker compose ps` — all 4 services should show `running`.

**Ingestion status stays `queued` forever**
The Worker is not connected to Redis. Check:
```bash
docker compose logs worker
```
Look for Redis connection errors. Make sure `REDIS_URL` in `.env` is correct.

**Chat returns 503 "Chat service error"**
Usually an expired or invalid `GROQ_API_KEY`. Verify:
```bash
docker compose logs app | findstr "CHAT ERROR"   # Windows
docker compose logs app | grep "CHAT ERROR"       # Mac/Linux
```

**Render deploy fails with "No start command"**
In the Render service settings → **Settings** tab → **Start Command** — make sure it says `bash start.sh` for the API and `bash worker.sh` for the Worker.

**Vercel frontend shows blank page or API errors**
Open browser DevTools → Console tab. Usually `NEXT_PUBLIC_API_URL` is wrong — make sure it points to your Render API URL (not worker URL) and has no trailing slash.

**Supabase storage upload fails**
Check that the bucket policy was set correctly in Phase 5, Step 27. The `anon` role must have INSERT permission with `WITH CHECK: true`.

**Google OAuth redirect fails in production**
You must add the exact production Vercel URL to Supabase Auth redirect URLs (Phase 11, Step 66). The URL must match exactly — no trailing slash.

---

## Useful Commands Reference

```bash
# Start local stack
docker compose up

# Start with fresh build
docker compose up --build

# View all logs
docker compose logs -f

# View specific service logs
docker compose logs -f app
docker compose logs -f worker

# Stop everything
docker compose down

# Stop and wipe all data (Qdrant collection cleared)
docker compose down -v

# Check running containers
docker compose ps

# Test API endpoints
curl http://localhost:8000/health
curl -X POST http://localhost:8000/ingest -F "file=@test.pdf"

# Frontend dev server
cd frontend && npm run dev

# Frontend production build (test before deploying)
cd frontend && npm run build && npm run start
```

---

## Service Dashboard URLs

Keep these bookmarked:

| Service | Dashboard |
|---|---|
| Groq (LLM) | [console.groq.com](https://console.groq.com) |
| Cohere (Embeddings) | [dashboard.cohere.com](https://dashboard.cohere.com) |
| Qdrant (Vector DB) | [cloud.qdrant.io](https://cloud.qdrant.io) |
| Upstash (Redis) | [console.upstash.com](https://console.upstash.com) |
| Supabase (Storage + Auth) | [supabase.com/dashboard](https://supabase.com/dashboard) |
| Render (Backend) | [dashboard.render.com](https://dashboard.render.com) |
| Vercel (Frontend) | [vercel.com/dashboard](https://vercel.com/dashboard) |
| UptimeRobot (Monitoring) | [uptimerobot.com/dashboard](https://uptimerobot.com/dashboard) |
```

---

## FILE: `.env.example`

```example
GROQ_API_KEY=your_groq_api_key_here
COHERE_API_KEY=your_cohere_api_key_here
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=rag_docs
REDIS_URL=redis://localhost:6379
UPLOAD_DIR=/tmp/rag_uploads
```

---

## FILE: `.gitignore`

```text
# Environment
.env
.env.local
.env*.local
.env.prod

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python

# Virtual environments
venv/
.venv/
env/

# Uploads and local data
uploads/
.qdrant/

# Next.js
.next/
node_modules/

# Model cache
.cache/
huggingface/
```

---

## FILE: `app/__init__.py`

```python

```

---

## FILE: `app/api/__init__.py`

```python

```

---

## FILE: `app/api/chat.py`

```python
from collections.abc import Awaitable, Callable

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, field_validator

from app.clients.groq_client import stream_llm
from app.clients.vector_store import search
from app.services.chat_services import handle_chat

router = APIRouter()


class ChatRequest(BaseModel):
    messages: list[dict]
    file_url: str

    @field_validator("messages")
    @classmethod
    def messages_not_empty(cls, v: list[dict]) -> list[dict]:
        if not v:
            raise ValueError("Messages list cannot be empty.")
        if v[-1].get("role") != "user":
            raise ValueError("Last message must be from the user.")
        if not v[-1].get("content", "").strip():
            raise ValueError("Last user message content cannot be empty.")
        return v


def get_chat_service() -> Callable[[list[dict], str], Awaitable[dict]]:
    return handle_chat


@router.post("/chat")
async def chat(
    request: ChatRequest,
    chat_service: Callable[[list[dict], str], Awaitable[dict]] = Depends(get_chat_service),
):
    try:
        return await chat_service(request.messages, request.file_url)
    except Exception as e:
        print(f"CHAT ERROR: {e}")
        raise HTTPException(status_code=503, detail=f"Chat service error: {str(e)}")


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    try:
        query = request.messages[-1]["content"] # Extract latest user query for retrieval
        context = search(query, file_url=request.file_url, top_k=3)
        if not context.strip():
            context = "No relevant context found."
        context = context[:1200]

        async def generate():
            async for token in stream_llm(context, request.messages):
                yield token

        return StreamingResponse(generate(), media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Stream error: {str(e)}")
```

---

## FILE: `app/api/ingest.py`

```python
import os
import re
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from rq.job import Job

from app.queues.ingest_job import enqueue_ingest, redis_conn
from app.clients.supabase_client import upload_file_to_supabase

router = APIRouter()


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for Supabase storage.
    - Remove/replace special characters that cause 400 errors
    - Add UUID prefix to ensure uniqueness
    """
    # Remove extension temporarily
    name_without_ext = filename.rsplit(".", 1)[0] if "." in filename else filename
    ext = filename.rsplit(".", 1)[1] if "." in filename else ""
    
    # Replace any character that isn't alphanumeric, dot, dash, or underscore
    clean_name = re.sub(r'[^a-zA-Z0-9.\-_]', '_', name_without_ext)
    
    # Add UUID prefix for uniqueness
    unique_id = uuid.uuid4().hex[:8]
    
    return f"{unique_id}_{clean_name}.{ext}" if ext else f"{unique_id}_{clean_name}"


@router.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    """
    Upload PDF to Supabase Storage, then enqueue for processing.
    Worker will download from Supabase URL and process.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        # Read file content
        file_content = await file.read()
        print(f"[API] File received: {file.filename} ({len(file_content)} bytes)")
        
        # Sanitize filename for Supabase
        clean_filename = sanitize_filename(file.filename)
        print(f"[API] Original filename: {file.filename} → Sanitized: {clean_filename}")
        
        # Upload to Supabase Storage
        storage_url = upload_file_to_supabase(file_content, clean_filename)
        print(f"[API] File uploaded to Supabase: {storage_url}")
        
        # Enqueue job with storage URL (not local path)
        job_id = enqueue_ingest(storage_url)
        print(f"[API] Job enqueued: {job_id}")
        
    except Exception as e:
        print(f"[API] Ingestion failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

    return {"job_id": job_id, "file": file.filename, "status": "queued", "storage_url": storage_url}


@router.get("/ingest/{job_id}/status")
async def ingest_status(job_id: str):
    try:
        job = Job.fetch(job_id, connection=redis_conn)
    except Exception:
        raise HTTPException(status_code=404, detail="Job not found.")

    return {"job_id": job_id, "status": job.get_status(), "error": job.exc_info}
```

---

## FILE: `app/api/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import chat, ingest, sources, suggestions

app = FastAPI(
    title="Scalable RAG Chatbot",
    description="Document ingestion and retrieval-augmented generation API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://rag-chatbot-sage.vercel.app", 
        "https://rag-chatbot-git-main-ishant2464s-projects.vercel.app",
        "https://rag-chatbot-bt19wswaf-ishant2464s-projects.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, tags=["Chat"])
app.include_router(ingest.router, tags=["Ingest"])
app.include_router(sources.router, tags=["Sources"])
app.include_router(suggestions.router, tags=["Suggestions"])


@app.get("/health")
@app.head("/health")
def health():
    return {"status": "ok"}
```

---

## FILE: `app/api/sources.py`

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from app.clients.vector_store import search_with_sources

router = APIRouter()

class SourcesRequest(BaseModel):
    query: str
    file_url: str

    @field_validator("query")
    @classmethod
    def query_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Query cannot be empty.")
        return v

@router.post("/chat/sources")
async def get_sources(request: SourcesRequest):
    try:
        result = search_with_sources(
            query=request.query,
            file_url=request.file_url,
            top_k=3
        )
        return {"sources": result["sources"]}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Sources error: {str(e)}")
```

---

## FILE: `app/api/suggestions.py`

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.clients.groq_client import generate_suggestions

router = APIRouter()

class SuggestionsRequest(BaseModel):
    messages: list[dict]
    file_url: str

@router.post("/chat/suggestions")
async def get_suggestions(request: SuggestionsRequest):
    try:
        suggestions = await generate_suggestions(request.messages)
        return {"suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Suggestions error: {str(e)}")
```

---

## FILE: `app/clients/__init__.py`

```python

```

---

## FILE: `app/clients/groq_client.py`

```python
from __future__ import annotations
import asyncio
import json
from groq import Groq
from app.core.config import settings

_client: Groq | None = None

def _get_client() -> Groq:
    global _client
    if _client is not None:
        return _client
    _client = Groq(api_key=settings.GROQ_API_KEY)
    return _client

def _generate_sync(context: str, messages: list[dict]) -> str:
    client = _get_client()

    llm_messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant. Answer questions using only the "
                "provided context from the uploaded document. Be concise and accurate. "
                "If the context does not contain enough information, say so honestly."
            )
        }
    ]

    for message in messages[:-1]:
        llm_messages.append({
            "role": message["role"],
            "content": message["content"]
        })

    last_user_msg = messages[-1]["content"]
    llm_messages.append({
        "role": "user",
        "content": f"Context from document:\n{context}\n\nQuestion: {last_user_msg}"
    })

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=llm_messages,
        temperature=0,
        max_tokens=512,
    )
    return response.choices[0].message.content.strip()

async def call_llm(context: str, messages: list[dict]) -> str:
    return await asyncio.to_thread(_generate_sync, context, messages)

from collections.abc import AsyncGenerator

async def stream_llm(context: str, messages: list[dict]) -> AsyncGenerator[str, None]:
    client = _get_client()

    llm_messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant. Answer questions using only the "
                "provided context from the uploaded document. Be concise and accurate. "
                "If the context does not contain enough information, say so honestly."
            )
        }
    ]

    for message in messages[:-1]:
        llm_messages.append({
            "role": message["role"],
            "content": message["content"]
        })

    last_user_msg = messages[-1]["content"]
    llm_messages.append({
        "role": "user",
        "content": f"Context from document:\n{context}\n\nQuestion: {last_user_msg}"
    })

    stream = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=llm_messages,
        temperature=0,
        max_tokens=512,
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta is not None:
            yield delta

def _generate_suggestions_sync(messages: list[dict]) -> list[str]:
    client = _get_client()
    
    # Take last 6 messages for context
    recent = messages[-6:] if len(messages) > 6 else messages
    
    # Build condensed conversation summary
    summary = ""
    for msg in recent:
        role = msg.get("role", "unknown").capitalize()
        content = msg.get("content", "")
        truncated = content[:200] if len(content) > 200 else content
        summary += f"{role}: {truncated}\n"
    
    llm_messages = [
        {
            "role": "system",
            "content": (
                "You generate follow-up questions for a document Q&A chatbot. Based on the conversation so far, "
                "suggest exactly 3 short, specific follow-up questions the user might want to ask next. "
                "Each question should be different and explore a new angle. "
                "Return ONLY a JSON array of 3 strings, nothing else. "
                "Example: [\"What are the key findings?\", \"How does this compare to previous results?\", \"What methodology was used?\"]"
            )
        },
        {
            "role": "user",
            "content": f"Conversation so far:\n{summary}\n\nGenerate 3 follow-up questions."
        }
    ]
    
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=llm_messages,
        temperature=0.7,
        max_tokens=200,
    )
    
    raw = response.choices[0].message.content.strip()
    
    # Try to parse as JSON
    try:
        suggestions = json.loads(raw)
        if isinstance(suggestions, list) and len(suggestions) >= 1:
            return [str(s) for s in suggestions[:3]]
    except json.JSONDecodeError:
        pass
    
    # Fallback: split by newlines and filter lines with '?'
    import re
    lines = raw.split('\n')
    questions = [re.sub(r'[^\w\s?.!]', '', line).strip() for line in lines if '?' in line]
    questions = [q for q in questions if q]
    if len(questions) >= 1:
        return questions[:3]
    
    # Last resort: default questions
    return [
        "Tell me more about this topic",
        "What are the key takeaways?",
        "Can you summarize the main points?"
    ]

async def generate_suggestions(messages: list[dict]) -> list[str]:
    return await asyncio.to_thread(_generate_suggestions_sync, messages)
```

---

## FILE: `app/clients/supabase_client.py`

```python
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
```

---

## FILE: `app/clients/vector_store.py`

```python
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


def search_with_sources(query: str, file_url: str, top_k: int = 4) -> dict:
    """
    Search for documents and return both the context string AND structured source metadata.
    """
    vector_store = get_vector_store()

    filter_condition = {
        "must": [
            {
                "key": "metadata.file_url",
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

    context_parts = []
    sources = []
    seen_pages = set()

    for r in results:
        context_parts.append(
            f"Page Content: {r.page_content}\n"
            f"Page Number: {r.metadata.get('page_label', 'N/A')}\n"
            f"Source: {r.metadata.get('source', 'Unknown')}"
        )

        page = r.metadata.get('page_label', 'N/A')
        if page not in seen_pages:
            seen_pages.add(page)
            sources.append({
                "page": page,
                "snippet": r.page_content[:150].strip() + "..." if len(r.page_content) > 150 else r.page_content.strip(),
                "source": r.metadata.get('source', 'Unknown')
            })

    context = "\n\n---\n\n".join(context_parts)

    return {
        "context": context,
        "sources": sources
    }


def ingest_documents(chunks, collection_name: str = QDRANT_COLLECTION):
    QdrantVectorStore.from_documents(
        documents=chunks,
        embedding=get_embedding_model(),
        url=QDRANT_URL,
        collection_name=collection_name,
        api_key=settings.QDRANT_API_KEY if settings.QDRANT_API_KEY else None,
        force_recreate=True
    )
```

---

## FILE: `app/core/__init__.py`

```python

```

---

## FILE: `app/core/config.py`

```python
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    LLM_MODEL: str = "distilgpt2"
    LLM_MAX_NEW_TOKENS: int = 150
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION: str = "rag_docs"
    QDRANT_API_KEY: str = ""
    COHERE_API_KEY: str = ""

    REDIS_URL: str = "redis://localhost:6379"
    RQ_JOB_TIMEOUT: int = 300
    UPLOAD_DIR: str = "/tmp/rag_uploads"
    
    # Supabase Storage
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_BUCKET: str = "rag-docs"


def ensure_upload_directory(upload_dir: str) -> None:
    Path(upload_dir).mkdir(parents=True, exist_ok=True)


settings = Settings()

# Validate required environment variables on startup
if not settings.GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is required")
if not settings.QDRANT_URL:
    raise ValueError("QDRANT_URL environment variable is required")

QDRANT_URL: str = settings.QDRANT_URL
QDRANT_COLLECTION: str = settings.QDRANT_COLLECTION
UPLOAD_DIR: str = settings.UPLOAD_DIR
LLM_MODEL: str = settings.LLM_MODEL
LLM_MAX_NEW_TOKENS: int = settings.LLM_MAX_NEW_TOKENS
EMBEDDING_MODEL: str = settings.EMBEDDING_MODEL
RQ_JOB_TIMEOUT: int = settings.RQ_JOB_TIMEOUT
ensure_upload_directory(settings.UPLOAD_DIR)
```

---

## FILE: `app/queues/__init__.py`

```python

```

---

## FILE: `app/queues/ingest_job.py`

```python
from redis import Redis
from app.core.config import settings
from rq import Queue
from app.services.ingest_service import process_document 

redis_conn = Redis.from_url(settings.REDIS_URL)
q = Queue(connection=redis_conn, default_timeout=settings.RQ_JOB_TIMEOUT)

def enqueue_ingest(storage_url: str) -> str:
    job = q.enqueue(process_document, storage_url, job_timeout=None)
    return job.id
```

---

## FILE: `app/queues/worker_tasks.py`

```python
import os

from app.services.ingest_service import process_document


def process_doc(file_path: str) -> None:
    if not os.path.isfile(file_path):
        raise FileNotFoundError(
            f"Ingestion file not found at worker path: {file_path}. "
            "Verify UPLOAD_DIR matches the shared Docker volume mount (expected /tmp/rag_uploads)."
        )

    process_document(file_path)
```

---

## FILE: `app/services/__init__.py`

```python

```

---

## FILE: `app/services/chat_services.py`

```python
from app.clients.vector_store import search
from app.clients.groq_client import call_llm

MAX_CHUNKS = 3
MAX_CHARS = 1200


async def handle_chat(messages: list[dict], file_url: str) -> dict:
    """
    Handle chat request for a specific document.
    Retrieves context only from the specified file_url.
    """
    query = messages[-1]["content"]

    print("\n--- CHAT REQUEST ---")
    print("QUERY:", query)
    print("FILE_URL:", file_url)

    context = search(query, file_url=file_url, top_k=MAX_CHUNKS)

    print("DOCS RETRIEVED:", len(context))

    if not context.strip():
        context = "No relevant context found."

    context = context[:MAX_CHARS]

    print("CONTEXT LENGTH:", len(context))
    print("CONTEXT PREVIEW:", context[:200])

    print("CALLING LLM...")

    answer = await call_llm(context, messages)

    print("LLM RESPONSE:", answer[:200])
    print("--- END REQUEST ---\n")

    return {"answer": answer}
```

---

## FILE: `app/services/ingest_service.py`

```python
import io
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
```

---

## FILE: `app/worker.py`

```python
from redis import Redis
from rq import Worker, Queue
from app.core.config import settings

redis_conn = Redis.from_url(settings.REDIS_URL)

if __name__ == "__main__":
    queue = Queue(connection=redis_conn)
    worker = Worker([queue], connection=redis_conn)
    worker.work()
```

---

## FILE: `app/worker_health.py`

```python
"""
Health check endpoint for worker service.
Verifies Redis connection is alive.
"""
from fastapi import FastAPI
from redis import Redis
from app.core.config import settings

app = FastAPI(title="Worker Health Check")


@app.get("/health")
def health():
    """
    Health check endpoint.
    Verifies RQ worker can connect to Redis.
    """
    try:
        redis_conn = Redis.from_url(settings.REDIS_URL)
        redis_conn.ping()
        return {
            "status": "worker-ok",
            "redis": "connected",
            "service": "rag-worker"
        }
    except Exception as e:
        print(f"[Health] Redis connection failed: {str(e)}")
        return {
            "status": "worker-degraded",
            "redis": "disconnected",
            "error": str(e),
            "service": "rag-worker"
        }, 503


@app.head("/health")
def health_head():
    """HEAD request support for health checks."""
    try:
        redis_conn = Redis.from_url(settings.REDIS_URL)
        redis_conn.ping()
        return {}
    except:
        return {}, 503
```

---

## FILE: `docker-compose.prod.yml`

```yaml
services:
  app:
    build: .
    ports:
      - "${PORT:-8000}:${PORT:-8000}"
    env_file:
      - .env.prod
    depends_on:
      - worker

  worker:
    build: .
    env_file:
      - .env.prod
    command: python -m app.worker
```

---

## FILE: `docker-compose.yml`

```yaml
services:

  vector-db:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

  valkey:
    image: valkey/valkey
    ports:
      - "6379:6379"

  app:
    build: .
    command: uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload
    ports:
      - "8000:8000"
    env_file:
      - .env
    environment:
      - QDRANT_URL=http://vector-db:6333
      - REDIS_URL=redis://valkey:6379
      - UPLOAD_DIR=/tmp/rag_uploads
    volumes:
      - ./app:/app/app
      - ./uploads:/tmp/rag_uploads
    depends_on:
      - vector-db
      - valkey

  worker:
    build: .
    command: python -m app.worker
    env_file:
      - .env
    environment:
      - QDRANT_URL=http://vector-db:6333
      - REDIS_URL=redis://valkey:6379
      - UPLOAD_DIR=/tmp/rag_uploads
    volumes:
      - ./uploads:/tmp/rag_uploads
    depends_on:
      - vector-db
      - valkey

volumes:
  qdrant_data:
```

---

## FILE: `Dockerfile`

```text
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY start.sh .
COPY worker.sh .
RUN chmod +x start.sh worker.sh

COPY app/ ./app/

ENV PYTHONPATH=/app

CMD ["bash", "start.sh"]
```

---

## FILE: `frontend/.env.example`

```example
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

---

## FILE: `frontend/next.config.js`

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {}
module.exports = nextConfig
```

---

## FILE: `frontend/package.json`

```json
{
  "name": "rag-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  },
  "dependencies": {
    "@supabase/supabase-js": "^2.106.1",
    "next": "14.2.3",
    "react": "^18",
    "react-dom": "^18",
    "react-markdown": "^9.0.1",
    "react-syntax-highlighter": "^15.5.0",
    "remark-gfm": "^4.0.0"
  },
  "devDependencies": {
    "@types/node": "^20",
    "@types/react": "^18",
    "@types/react-dom": "^18",
    "@types/react-syntax-highlighter": "^15.5.11",
    "autoprefixer": "^10.0.1",
    "postcss": "^8",
    "tailwindcss": "^3.3.0",
    "typescript": "^5"
  }
}
```

---

## FILE: `frontend/postcss.config.js`

```javascript
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

---

## FILE: `frontend/src/app/components/AuthProvider.tsx`

```tsx
'use client'

import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { supabase } from '@/lib/supabase'
import { User, Session } from '@supabase/supabase-js'

interface AuthContextType {
  user: User | null
  session: Session | null
  loading: boolean
  signInWithGoogle: () => Promise<void>
  signOut: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [session, setSession] = useState<Session | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session)
      setUser(session?.user ?? null)
      setLoading(false)
    })

    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        setSession(session)
        setUser(session?.user ?? null)
        setLoading(false)
      }
    )

    return () => subscription.unsubscribe()
  }, [])

  const signInWithGoogle = async () => {
    await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: window.location.origin,
      },
    })
  }

  const signOut = async () => {
    await supabase.auth.signOut()
  }

  return (
    <AuthContext.Provider value={{ user, session, loading, signInWithGoogle, signOut }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
```

---

## FILE: `frontend/src/app/components/ChatWindow.tsx`

```tsx
'use client'

import { useState, useRef, useEffect, KeyboardEvent } from 'react'
import MessageBubble from './MessageBubble'

interface Source {
  page: string
  snippet: string
  source: string
}

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: Source[]
  suggestions?: string[]
}

interface Props {
  fileUrl: string
}

export default function ChatWindow({ fileUrl }: Props) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '0',
      role: 'assistant',
      content: 'Document loaded. Ask me anything about it.',
    },
  ])
  const [input, setInput] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)
  const API = process.env.NEXT_PUBLIC_API_URL || 'https://rag-chatbot-d3wz.onrender.com'

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function executeSend(query: string) {
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: query,
    }

    const assistantId = (Date.now() + 1).toString()
    const assistantMessage: Message = {
      id: assistantId,
      role: 'assistant',
      content: '',
    }

    // Prepare messages for the backend, filtering out the initial welcome message
    // and limiting to the last 20 messages for context window management.
    const allMessages = [...messages.filter(m => m.id !== '0'), userMessage]
    const recentMessages = allMessages.slice(-20) // Limit to last 20 messages

    const payloadMessages = recentMessages.map(m => ({
      role: m.role,
      content: m.content
    }))

    setMessages((prev) => [...prev, userMessage, assistantMessage])
    setIsStreaming(true)

    // Start sources fetch (non-blocking, parallel to streaming)
    fetch(`${API}/chat/sources`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, file_url: fileUrl }),
    })
      .then(res => res.json())
      .then(data => {
        if (data.sources) {
          setMessages(prev =>
            prev.map(m =>
              m.id === assistantId ? { ...m, sources: data.sources } : m
            )
          )
        }
      })
      .catch(err => console.error('Sources fetch error:', err))

    // Start suggestions fetch (non-blocking, parallel to streaming)
    fetch(`${API}/chat/suggestions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: payloadMessages, file_url: fileUrl }),
    })
      .then(res => res.json())
      .then(data => {
        if (data.suggestions) {
          setMessages(prev =>
            prev.map(m =>
              m.id === assistantId ? { ...m, suggestions: data.suggestions } : m
            )
          )
        }
      })
      .catch(err => console.error('Suggestions fetch error:', err))

    try {
      const res = await fetch(`${API}/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: payloadMessages,
          file_url: fileUrl,
        }),
      })

      if (!res.ok) throw new Error('Stream request failed')
      if (!res.body) throw new Error('No response body')

      const reader = res.body.getReader()
      const decoder = new TextDecoder()

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value, { stream: true })
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId ? { ...m, content: m.content + chunk } : m
          )
        )
      }
    } catch (err) {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId
            ? { ...m, content: 'Something went wrong. Please try again.' }
            : m
        )
      )
    } finally {
      setIsStreaming(false)
    }
  }

  function sendMessage() {
    if (!input.trim() || isStreaming) return
    executeSend(input.trim())
    setInput('')
  }

  function handleSuggestionClick(suggestion: string) {
    if (!isStreaming) {
      executeSend(suggestion)
    }
  }

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  function exportChat() {
    const chatContent = messages
      .filter(m => m.id !== '0') // Skip welcome message
      .map(m => {
        const role = m.role === 'user' ? '## 🧑 You' : '## 🤖 AI'
        let text = `${role}\n\n${m.content}`
        if (m.sources && m.sources.length > 0) {
          text += '\n\n**Sources:** ' + m.sources.map(s => `Page ${s.page}`).join(', ')
        }
        return text
      })
      .join('\n\n---\n\n')

    const header = `# RAG Chatbot Conversation\n\nExported: ${new Date().toLocaleString()}\n\n---\n\n`
    const fullContent = header + chatContent

    const blob = new Blob([fullContent], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `rag-chat-${new Date().toISOString().slice(0, 10)}.md`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      <div className="flex items-center justify-between px-6 py-2 border-b border-gray-800">
        <span className="text-xs text-gray-500">Chat with your document</span>
        <button
          onClick={exportChat}
          disabled={messages.filter(m => m.id !== '0').length === 0 || isStreaming}
          className="text-xs text-gray-400 hover:text-white flex items-center gap-1.5 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
          title="Export chat as Markdown"
        >
          <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Export
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-6 py-6">
        <div className="mx-auto max-w-2xl space-y-6">
          {messages.map((m, i) => (
            <MessageBubble
              key={m.id}
              role={m.role}
              content={m.content}
              sources={m.sources}
              suggestions={m.suggestions}
              isStreaming={isStreaming && i === messages.length - 1 && m.role === 'assistant'}
              isLastAssistant={m.role === 'assistant' && i === messages.length - 1}
              onSuggestionClick={handleSuggestionClick}
            />
          ))}
          <div ref={bottomRef} />
        </div>
      </div>

      <div className="border-t border-gray-800 px-6 py-4">
        <div className="mx-auto max-w-2xl">
          <div className="flex gap-3 items-end">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask a question... (Enter to send)"
              rows={1}
              disabled={isStreaming}
              className="
                flex-1 resize-none rounded-xl bg-gray-800 px-4 py-3 text-sm text-gray-100
                placeholder-gray-500 outline-none focus:ring-1 focus:ring-blue-500
                disabled:opacity-50 max-h-32 overflow-y-auto
              "
              style={{ minHeight: '44px' }}
            />
            <button
              onClick={sendMessage}
              disabled={!input.trim() || isStreaming}
              className="
                flex h-11 w-11 shrink-0 items-center justify-center rounded-xl
                bg-blue-600 text-white transition-colors
                hover:bg-blue-500 disabled:opacity-40 disabled:cursor-not-allowed
              "
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M6 12 3.269 3.125A59.769 59.769 0 0 1 21.485 12 59.768 59.768 0 0 1 3.27 20.875L5.999 12Zm0 0h7.5" />
              </svg>
            </button>
          </div>
          <p className="mt-2 text-xs text-gray-600 text-center">
            Shift+Enter for new line
          </p>
        </div>
      </div>
    </div>
  )
}
```

---

## FILE: `frontend/src/app/components/DocumentSidebar.tsx`

```tsx
'use client'

interface Document {
  url: string
  name: string
  uploadedAt: string
}

interface Props {
  documents: Document[]
  activeUrl: string | null
  onSelectDocument: (url: string) => void
  onNewUpload: () => void
}

function formatDate(isoString: string): string {
  const date = new Date(isoString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  return date.toLocaleDateString()
}

export default function DocumentSidebar({
  documents,
  activeUrl,
  onSelectDocument,
  onNewUpload,
}: Props) {
  return (
    <div className="flex w-64 flex-col border-r border-gray-800 bg-gray-900">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-800 p-4">
        <h2 className="text-sm font-semibold text-white">📚 Documents</h2>
        <button
          onClick={onNewUpload}
          className="text-xs bg-blue-600 hover:bg-blue-500 text-white rounded-lg px-3 py-1.5 transition-colors font-medium"
        >
          Upload New
        </button>
      </div>

      {/* Document List */}
      <div className="flex-1 overflow-y-auto p-2">
        {documents.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <p className="text-sm text-gray-500 mb-1">No documents yet</p>
            <p className="text-xs text-gray-600">Upload your first PDF to get started</p>
          </div>
        ) : (
          <div className="space-y-1">
            {documents.map((doc) => (
              <button
                key={doc.url}
                onClick={() => onSelectDocument(doc.url)}
                className={`w-full text-left flex items-start gap-2 rounded-lg px-3 py-2.5 transition-colors ${
                  activeUrl === doc.url
                    ? 'bg-gray-800 border-l-2 border-blue-500'
                    : 'hover:bg-gray-800/50'
                }`}
              >
                <span className="shrink-0 text-lg">📄</span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-200 truncate">{doc.name}</p>
                  <p className="text-xs text-gray-500">{formatDate(doc.uploadedAt)}</p>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
```

---

## FILE: `frontend/src/app/components/FileUpload.tsx`

```tsx
'use client'

import { useState, useRef, DragEvent, ChangeEvent } from 'react'

interface Props {
  onSuccess: (url: string, fileName: string) => void
}

type Status = 'idle' | 'uploading' | 'polling' | 'done' | 'error'

export default function FileUpload({ onSuccess }: Props) {
  const [status, setStatus] = useState<Status>('idle')
  const [message, setMessage] = useState('')
  const [isDragging, setIsDragging] = useState(false)
  const [fileName, setFileName] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)
  const API = process.env.NEXT_PUBLIC_API_URL

  async function uploadFile(file: File) {
    if (!file.name.endsWith('.pdf')) {
      setStatus('error')
      setMessage('Only PDF files are supported.')
      return
    }

    setFileName(file.name)
    setStatus('uploading')
    setMessage('Uploading...')

    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await fetch(`${API}/ingest`, {
        method: 'POST',
        body: formData,
      })
      const data = await res.json()

      if (!res.ok) {
        throw new Error(data.detail || 'Upload failed')
      }

      setStatus('polling')
      setMessage('Processing document...')
      // Pass the storage URL to the new pollStatus function
      pollStatus(data.job_id, data.storage_url) 
    } catch (err: unknown) {
      setStatus('error')
      setMessage(err instanceof Error ? err.message : 'Upload failed')
    }
  }

  async function pollStatus(jobId: string, storageUrl: string) {
    for (let i = 0; i < 300; i++) {
      try {
        const res = await fetch(`${API}/ingest/${jobId}/status`)
        const data = await res.json()

        if (data.status === 'finished') {
          setStatus('done')
          setMessage('✅ Document ready!')
          // Pass the URL and filename up to the parent page.tsx
          setTimeout(() => onSuccess(storageUrl, fileName), 800) 
          return
        }

        if (data.status === 'failed') {
          setStatus('error')
          setMessage(`Processing failed: ${data.error}`)
          return
        }
      } catch (err) {
        console.error('Poll error:', err)
      }

      // Wait 1 second before trying again
      await new Promise((resolve) => setTimeout(resolve, 1000))
    }

    setStatus('error')
    setMessage('Processing timeout')
  }

  function handleDrop(e: DragEvent<HTMLDivElement>) {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) uploadFile(file)
  }

  function handleChange(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (file) uploadFile(file)
  }

  const isLoading = status === 'uploading' || status === 'polling'

  return (
    <div className="w-full max-w-lg">
      <div
        onClick={() => !isLoading && inputRef.current?.click()}
        onDrop={handleDrop}
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
        onDragLeave={() => setIsDragging(false)}
        className={`
          relative flex flex-col items-center justify-center gap-4 rounded-xl border-2 border-dashed p-12
          transition-colors cursor-pointer
          ${isDragging ? 'border-blue-400 bg-blue-950/30' : 'border-gray-700 bg-gray-900 hover:border-gray-500'}
          ${isLoading ? 'cursor-not-allowed opacity-70' : ''}
        `}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf"
          className="hidden"
          onChange={handleChange}
          disabled={isLoading}
        />

        {status === 'idle' && (
          <>
            <div className="rounded-full bg-gray-800 p-4">
              <svg className="h-8 w-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                  d="M12 16.5V9.75m0 0 3 3m-3-3-3 3M6.75 19.5a4.5 4.5 0 0 1-1.41-8.775 5.25 5.25 0 0 1 10.233-2.33 3 3 0 0 1 3.758 3.848A3.752 3.752 0 0 1 18 19.5H6.75Z" />
              </svg>
            </div>
            <div className="text-center">
              <p className="text-base font-medium text-gray-200">Drop your PDF here</p>
              <p className="mt-1 text-sm text-gray-500">or click to browse</p>
            </div>
          </>
        )}

        {isLoading && (
          <>
            <div className="h-10 w-10 animate-spin rounded-full border-2 border-gray-700 border-t-blue-400" />
            <div className="text-center">
              <p className="text-sm font-medium text-gray-200">{fileName}</p>
              <p className="mt-1 text-sm text-gray-400">{message}</p>
            </div>
          </>
        )}

        {status === 'done' && (
          <>
            <div className="rounded-full bg-green-900/50 p-4">
              <svg className="h-8 w-8 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <p className="text-sm text-green-400">{message}</p>
          </>
        )}

        {status === 'error' && (
          <>
            <div className="rounded-full bg-red-900/50 p-4">
              <svg className="h-8 w-8 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <p className="text-sm text-red-400">{message}</p>
            <button
              onClick={(e) => { e.stopPropagation(); setStatus('idle'); setMessage('') }}
              className="text-xs text-gray-500 underline hover:text-gray-300"
            >
              Try again
            </button>
          </>
        )}
      </div>
    </div>
  )
}
```

---

## FILE: `frontend/src/app/components/LoginScreen.tsx`

```tsx
'use client'

import { useAuth } from './AuthProvider'

export default function LoginScreen() {
  const { signInWithGoogle, loading } = useAuth()

  return (
    <div className="flex h-full items-center justify-center">
      <div className="w-full max-w-md text-center space-y-8 p-8">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">RAG Chatbot</h1>
          <p className="text-gray-400">Upload documents and ask questions powered by AI</p>
        </div>

        <div className="space-y-4">
          <button
            onClick={signInWithGoogle}
            disabled={loading}
            className="
              w-full flex items-center justify-center gap-3 rounded-xl
              bg-white text-gray-900 px-6 py-3 font-medium
              hover:bg-gray-100 transition-colors
              disabled:opacity-50 disabled:cursor-not-allowed
            "
          >
            <svg className="h-5 w-5" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" />
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
            </svg>
            Continue with Google
          </button>
        </div>

        <p className="text-xs text-gray-600">
          By signing in, you agree to our Terms of Service
        </p>
      </div>
    </div>
  )
}
```

---

## FILE: `frontend/src/app/components/MessageBubble.tsx`

```tsx
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'

interface Source {
  page: string
  snippet: string
  source: string
}

interface Props {
  role: 'user' | 'assistant'
  content: string
  sources?: Source[]
  suggestions?: string[]
  isStreaming?: boolean
  isLastAssistant?: boolean
  onSuggestionClick?: (suggestion: string) => void
}

export default function MessageBubble({ role, content, sources, suggestions, isStreaming, isLastAssistant, onSuggestionClick }: Props) {
  const isUser = role === 'user'

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
      <div className={`
        flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-semibold
        ${isUser ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300'}
      `}>
        {isUser ? 'You' : 'AI'}
      </div>

      <div className={`
        max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed
        ${isUser
          ? 'bg-blue-600 text-white rounded-tr-sm'
          : 'bg-gray-800 text-gray-100 rounded-tl-sm'
        }
      `}>
        {isUser ? (
          content
        ) : (
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              code({ node, inline, className, children, ...props }: any) {
                const match = /language-(\w+)/.exec(className || '')
                return !inline && match ? (
                  <SyntaxHighlighter
                    style={oneDark}
                    language={match[1]}
                    PreTag="div"
                    customStyle={{
                      margin: '0.5rem 0',
                      borderRadius: '0.5rem',
                      fontSize: '0.8rem',
                    }}
                    {...props}
                  >
                    {String(children).replace(/\n$/, '')}
                  </SyntaxHighlighter>
                ) : (
                  <code
                    className="bg-gray-700 text-gray-200 px-1.5 py-0.5 rounded text-sm font-mono"
                    {...props}
                  >
                    {children}
                  </code>
                )
              },
              p({ children }: any) {
                return <p className="mb-2 last:mb-0">{children}</p>
              },
              ul({ children }: any) {
                return <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>
              },
              ol({ children }: any) {
                return <ol className="list-decimal list-inside mb-2 space-y-1">{children}</ol>
              },
              li({ children }: any) {
                return <li className="ml-2">{children}</li>
              },
              h1({ children }: any) {
                return <h1 className="text-lg font-bold mb-2">{children}</h1>
              },
              h2({ children }: any) {
                return <h2 className="text-base font-bold mb-2">{children}</h2>
              },
              h3({ children }: any) {
                return <h3 className="text-sm font-bold mb-1">{children}</h3>
              },
              blockquote({ children }: any) {
                return (
                  <blockquote className="border-l-2 border-gray-500 pl-3 italic text-gray-300 mb-2">
                    {children}
                  </blockquote>
                )
              },
              table({ children }: any) {
                return (
                  <div className="overflow-x-auto mb-2">
                    <table className="min-w-full text-sm border border-gray-600">
                      {children}
                    </table>
                  </div>
                )
              },
              thead({ children }: any) {
                return <thead className="bg-gray-700">{children}</thead>
              },
              th({ children }: any) {
                return <th className="px-3 py-1 text-left font-semibold border border-gray-600">{children}</th>
              },
              td({ children }: any) {
                return <td className="px-3 py-1 border border-gray-600">{children}</td>
              },
              a({ href, children }: any) {
                return (
                  <a href={href} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline">
                    {children}
                  </a>
                )
              },
              strong({ children }: any) {
                return <strong className="font-semibold text-white">{children}</strong>
              },
              em({ children }: any) {
                return <em className="italic text-gray-300">{children}</em>
              },
              hr() {
                return <hr className="border-gray-600 my-2" />
              },
            }}
          >
            {content}
          </ReactMarkdown>
        )}
        {isStreaming && (
          <span className="ml-0.5 inline-block h-4 w-0.5 animate-pulse bg-current opacity-70" />
        )}
        {!isUser && sources && sources.length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-700">
            <p className="text-xs text-gray-400 mb-2 font-medium">📄 Sources</p>
            <div className="flex flex-wrap gap-2">
              {sources.map((source, index) => (
                <div
                  key={index}
                  className="group relative"
                >
                  <div className="inline-flex items-center gap-1.5 rounded-lg bg-gray-700/50 px-2.5 py-1.5 text-xs text-gray-300 hover:bg-gray-700 hover:text-white transition-colors cursor-default">
                    <span className="text-blue-400">📄</span>
                    <span>Page {source.page}</span>
                  </div>
                  {/* Tooltip with snippet on hover */}
                  <div className="absolute bottom-full left-0 mb-2 hidden group-hover:block z-50 w-64 p-3 rounded-lg bg-gray-900 border border-gray-700 shadow-xl">
                    <p className="text-xs text-gray-400 mb-1 font-medium">Page {source.page}</p>
                    <p className="text-xs text-gray-300 leading-relaxed">{source.snippet}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        {!isUser && isLastAssistant && !isStreaming && suggestions && suggestions.length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-700">
            <p className="text-xs text-gray-400 mb-2 font-medium">💡 Follow-up questions</p>
            <div className="flex flex-col gap-1.5">
              {suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => onSuggestionClick?.(suggestion)}
                  className="text-left text-xs text-blue-400 hover:text-blue-300 hover:bg-gray-700/50 rounded-lg px-2.5 py-1.5 transition-colors"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
```

---

## FILE: `frontend/src/app/globals.css`

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Markdown content styling */
.markdown-content pre {
  margin: 0;
}
```

---

## FILE: `frontend/src/app/layout.tsx`

```tsx
import type { Metadata } from 'next'
import './globals.css'
import { AuthProvider } from './components/AuthProvider'

export const metadata: Metadata = {
  title: 'RAG Chatbot',
  description: 'Ask questions about your documents',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="h-full">
      <body className="h-full bg-gray-950 text-gray-100 antialiased">
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  )
}
```

---

## FILE: `frontend/src/app/page.tsx`

```tsx
'use client'

import { useState, useEffect } from 'react'
import { useAuth } from './components/AuthProvider'
import LoginScreen from './components/LoginScreen'
import DocumentSidebar from './components/DocumentSidebar'
import FileUpload from './components/FileUpload'
import ChatWindow from './components/ChatWindow'

interface Document {
  url: string
  name: string
  uploadedAt: string
}

export default function Home() {
  const { user, loading, signOut } = useAuth()
  const [fileUrl, setFileUrl] = useState<string | null>(null)
  const [documents, setDocuments] = useState<Document[]>([])
  const [showUpload, setShowUpload] = useState(false)

  // Load documents from localStorage on mount (per-user)
  useEffect(() => {
    if (user) {
      const saved = localStorage.getItem(`rag-docs-${user.id}`)
      if (saved) {
        try {
          setDocuments(JSON.parse(saved))
        } catch {}
      }
    }
  }, [user])

  // Save documents to localStorage when they change
  useEffect(() => {
    if (user && documents.length > 0) {
      localStorage.setItem(`rag-docs-${user.id}`, JSON.stringify(documents))
    }
  }, [documents, user])

  // Handle new document upload success
  function handleUploadSuccess(url: string, fileName: string) {
    const newDoc: Document = {
      url,
      name: fileName,
      uploadedAt: new Date().toISOString(),
    }
    setDocuments((prev) => [newDoc, ...prev])
    setFileUrl(url)
    setShowUpload(false)
  }

  // Handle document selection from sidebar
  function handleSelectDocument(url: string) {
    setFileUrl(url)
    setShowUpload(false)
  }

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-gray-700 border-t-blue-400" />
      </div>
    )
  }

  if (!user) {
    return <LoginScreen />
  }

  return (
    <div className="flex h-full flex-col">
      <header className="border-b border-gray-800 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-white">RAG Chatbot</h1>
            <p className="text-sm text-gray-400">Upload a PDF and ask questions about it</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className={`h-2 w-2 rounded-full ${fileUrl ? 'bg-green-400' : 'bg-gray-600'}`} />
              <span className="text-sm text-gray-400">
                {fileUrl ? 'Document ready' : 'No document loaded'}
              </span>
            </div>
            <div className="flex items-center gap-3 border-l border-gray-700 pl-4">
              {user.user_metadata?.avatar_url && (
                <img
                  src={user.user_metadata.avatar_url}
                  alt="Profile"
                  className="h-7 w-7 rounded-full"
                />
              )}
              <span className="text-sm text-gray-300">
                {user.user_metadata?.full_name || user.email}
              </span>
              <button
                onClick={signOut}
                className="text-xs text-gray-500 hover:text-gray-300 transition-colors"
              >
                Sign out
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        <DocumentSidebar
          documents={documents}
          activeUrl={fileUrl}
          onSelectDocument={handleSelectDocument}
          onNewUpload={() => setShowUpload(true)}
        />
        <main className="flex flex-1 overflow-hidden">
          <div className="flex w-full flex-col">
            {showUpload || !fileUrl ? (
              <div className="flex flex-1 items-center justify-center p-8">
                <FileUpload onSuccess={handleUploadSuccess} />
              </div>
            ) : (
              <ChatWindow key={fileUrl} fileUrl={fileUrl} />
            )}
          </div>
        </main>
      </div>
    </div>
  )
}
```

---

## FILE: `frontend/src/lib/supabase.ts`

```typescript
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
```

---

## FILE: `frontend/tailwind.config.js`

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

---

## FILE: `frontend/tsconfig.json`

```json
{
  "compilerOptions": {
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": { "@/*": ["./src/*"] }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

---

## FILE: `INTERVIEW_NOTES.md`

```markdown
# RAG Project Interview Notes

This guide is tailored to your current codebase and is meant for quick revision.
Use it to explain architecture clearly, justify design decisions, and answer follow-up questions.
Focus on understanding "why" each layer exists, not only "what" each file does.

## 1) 60-Second Project Pitch

This is a FastAPI-based RAG system where users upload PDF documents, those documents are processed in the background, chunked, embedded, and stored in Qdrant for semantic retrieval.  
When a user asks a question, the system retrieves relevant chunks from Qdrant and sends both the question and retrieved context to a local Hugging Face text-generation model to synthesize an answer.

## 2) Codebase Mental Model

- `app/api/`: HTTP entry points (`/ingest`, `/chat`, `/health`)
- `app/services/`: business logic orchestration (ingestion flow and chat flow)
- `app/clients/`: integrations (Qdrant vector DB + local Hugging Face generation client)
- `app/queues/`: enqueue functions + worker task boundary
- `app/worker.py`: long-running background worker process
- `app/core/config.py`: typed settings from environment variables / `.env`
- `Dockerfile` + `docker-compose.yml`: local multi-service runtime (API, worker, Qdrant, Valkey)

## 3) End-to-End Data Flows

### A) Document Ingestion Flow
1. User calls `POST /ingest` with a PDF file.
2. API validates extension and saves file to `UPLOAD_DIR`.
3. API enqueues a background job with file path.
4. Worker picks job from queue.
5. Ingestion service loads PDF pages.
6. Text splitter creates overlapping chunks.
7. Vector client embeds chunks and stores vectors in Qdrant.
8. Document is now searchable for future chat.

### B) Chat Question Flow
1. User calls `POST /chat` with a query.
2. Chat service triggers vector search.
3. Query text is embedded to a vector.
4. Qdrant returns top-k nearest chunks.
5. Retrieved chunks are formatted into context.
6. LLM client sends context + query to model.
7. Model returns grounded answer.
8. API returns answer JSON to user.

## 4) Key Concepts You Must Be Able to Explain

- **RAG:** Retrieval + Generation. Retrieval finds evidence; generation synthesizes answer.
- **Embedding:** Numeric vector representation of text meaning.
- **Search query:** Raw natural-language user question before vector conversion.
- **Vector similarity search:** Finds chunks semantically closest to query embedding.
- **Chunk overlap:** Repeats boundary text across chunks to preserve context continuity.
- **Async + blocking work:** Use `async/await` for concurrency-friendly code paths, and offload blocking CPU/GPU work (local model inference) to threads/processes so the event loop stays responsive.
- **Queue + worker:** Offloads long tasks from request lifecycle to avoid timeouts.
- **Dependency Injection (`Depends`):** FastAPI injects dependencies before route executes.
- **Serialization:** Converting task args into storable/transmittable format for queue transport.
- **Eventual consistency:** Uploaded docs may not be instantly searchable until worker completes.

## 5) Top 20 Interview Questions with Strong Answers

1. **Why not process ingestion directly inside `POST /ingest`?**  
   Ingestion is heavy (PDF parsing, chunking, embeddings, DB writes). Doing it inline blocks requests and risks timeout. Queue + worker keeps API responsive and scales background throughput independently.

2. **What is the difference between an embedding and a search query?**  
   Search query is plain text from user. Embedding is a dense numeric vector representation of that text used for similarity math in vector DB.

3. **How does RAG reduce hallucination?**  
   It provides retrieved context from trusted docs and constrains the model prompt to answer from that context.

4. **Why chunk documents? Why overlap?**  
   Long docs exceed practical context lengths and retrieval granularity. Chunking creates searchable units; overlap preserves meaning near chunk boundaries.

5. **How does `POST /chat` connect to the rest of the stack?**  
   Route calls chat service -> vector search retrieves context -> LLM client generates answer -> route returns response.

6. **Why use async in chat path?**  
   Even with a local model, generation is still blocking CPU work. `async/await` lets the route be async-friendly while the actual inference runs in a thread pool (`asyncio.to_thread`) so other requests are not blocked on the event loop.

7. **What does `Depends` do in plain English?**  
   FastAPI runs dependency function first, then injects its return value into route params. It improves testability and separation of concerns.

8. **What is serialization in queue systems?**  
   Task function + arguments are encoded into a storable form in Redis. Worker later decodes and executes them.

9. **Why pass only `file_path` into job payload?**  
   Simple payloads serialize reliably, are lightweight, and avoid large-message overhead.

10. **How is the worker independent from FastAPI?**  
    Worker runs as separate process/container (`python -m app.worker`) and continuously polls queue. API and worker communicate through Redis, not direct calls.

11. **What role does Qdrant play?**  
    It stores embeddings and performs nearest-neighbor retrieval for semantic search.

12. **Why centralize config in `BaseSettings`?**  
    Typed, validated, centralized env loading reduces config bugs and keeps all services aligned.

13. **How do environment variables reach Python code?**  
    `.env` is read by settings config, values become fields on a settings object, then imported where needed.

14. **Why separate API, services, and clients?**  
    Routes handle HTTP concerns, services orchestrate business flow, clients isolate external APIs/DB SDKs. This improves maintainability and testing.

15. **What are failure points in this architecture?**  
    Model download/load failures, CPU/RAM pressure (OOM), slow inference latency, Qdrant unavailability, Redis downtime, malformed PDFs, queue backlog. Add retries, health checks, and observability.

16. **What does `GET /health` prove?**  
    Basic app liveness. It does not guarantee downstream dependency health unless expanded.

17. **How would you track ingestion progress by `job_id`?**  
    Expose job-status endpoint querying RQ states (queued/started/finished/failed) and return timestamps/errors.

18. **How would you improve answer quality?**  
    Better chunk strategy, metadata filtering, hybrid retrieval, reranking, prompt refinement, and citation formatting.

19. **How would you scale this system?**  
    Replicate API containers for read traffic, scale worker replicas for ingest throughput, monitor queue depth and model latency.

20. **What trade-off does queue-based ingestion introduce?**  
    Eventual consistency: newly uploaded docs may not be instantly available until background job completes.

## 6) Quick "Explain It to Interviewer" Scripts

### Script: "How does your ingestion work?"
"Our ingestion endpoint only validates and stores the uploaded PDF, then enqueues a job. A separate worker consumes that job, parses the PDF, splits text into overlapping chunks, generates embeddings, and stores vectors in Qdrant. This keeps API latency low and prevents request timeouts."

### Script: "How do you answer questions?"
"At query time, we embed the user question and run vector similarity search in Qdrant to fetch relevant chunks. We format a prompt with that context and run a local Hugging Face text-generation model to produce an answer. For production, you would typically pick a stronger instruction-tuned model and add evaluation for faithfulness."

### Script: "Why this architecture?"
"We separated API, services, clients, and worker layers to improve clarity and scalability. API handles HTTP, services orchestrate flow, clients isolate external systems, and workers handle heavy async tasks. This design is easier to test, reason about, and scale."

## 7) Final Revision Checklist (Before Interview)

- Can explain ingestion and chat flows without looking at code.
- Can define embedding vs query in one sentence each.
- Can explain why queue + worker improves reliability and UX.
- Can explain `async/await` in terms of non-blocking I/O.
- Can explain `Depends` as dependency injection and testing aid.
- Can discuss at least 3 realistic failure modes and improvements.
```

---

## FILE: `requirements.txt`

```text
#
# FastAPI
#
fastapi==0.116.1
uvicorn[standard]==0.35.0
python-multipart==0.0.20
python-dotenv==1.1.1
pydantic==2.11.7
pydantic-settings==2.4.0

#
# RAG / Retrieval
#
langchain==0.3.27
langchain-community==0.3.27
langchain-cohere
langchain-qdrant==0.2.0
langchain-text-splitters==0.3.9
qdrant-client==1.17.1
cohere
groq

#
# Queue
#
redis==6.4.0
rq==2.3.2

#
# Storage
#
supabase==2.30.0
httpx>=0.28.0
requests==2.32.3

#
# Docs
#
pypdf==5.9.0
```

---

## FILE: `start.sh`

```bash
#!/bin/bash
set -e
exec uvicorn app.api.main:app --host 0.0.0.0 --port $PORT
```

---

## FILE: `worker.sh`

```bash
#!/bin/bash
set -e

cd /app

# Start RQ worker in background
python -m app.worker &
WORKER_PID=$!

# Start health check endpoint to satisfy Render port requirement
# Verifies Redis connection is alive
python -m uvicorn app.worker_health:app --host 0.0.0.0 --port 8000 &
HEALTH_PID=$!

# If either process dies, exit container so Render restarts it
wait -n
exit 1
```

---
