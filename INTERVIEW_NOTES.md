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

