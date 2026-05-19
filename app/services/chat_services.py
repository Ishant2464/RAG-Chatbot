from app.clients.vector_store import search
from app.clients.openai_client import call_llm

MAX_CHUNKS = 3
MAX_CHARS = 1200


async def handle_chat(query: str) -> dict:
    print("\n--- CHAT REQUEST ---")
    print("QUERY:", query)


    docs = search(query, top_k=MAX_CHUNKS)

    print("DOCS RETRIEVED:", len(docs) if isinstance(docs, list) else "unknown")

    if isinstance(docs, list):
        context = "\n".join(
            d.page_content if hasattr(d, "page_content") else str(d)
            for d in docs
        )
    else:
        context = str(docs)

    if not context.strip():
        context = "No relevant context found."

    context = context[:MAX_CHARS]

    print("CONTEXT LENGTH:", len(context))
    print("CONTEXT PREVIEW:", context[:200])

    print("CALLING LLM...")

    answer = await call_llm(context, query)

    print("LLM RESPONSE:", answer[:200])
    print("--- END REQUEST ---\n")

    return {"answer": answer}
