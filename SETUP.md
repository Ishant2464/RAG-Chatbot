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