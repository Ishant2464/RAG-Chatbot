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
