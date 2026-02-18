from openai import AsyncOpenAI

from app.config import settings
from app.db.collections import knowledge_base_col

_openai_client: AsyncOpenAI | None = None


def _get_openai_client() -> AsyncOpenAI: # TODO: Cambiar la obtención del cliente a OpenRouter
    global _openai_client
    if _openai_client is None:
        _openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    return _openai_client


async def generate_embedding(text: str) -> list[float]:
    client = _get_openai_client()
    response = await client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return response.data[0].embedding


async def vector_search(
    query_embedding: list[float],
    scope: str,
    top_k: int = 5,
) -> list[dict]:
    col = knowledge_base_col()

    if scope == "global":
        filter_stage = {"scope": {"$in": ["jonathan", "pablo"]}}
    else:
        filter_stage = {"scope": scope}

    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": top_k * 10,
                "limit": top_k,
                "filter": filter_stage,
            }
        },
        {
            "$project": {
                "_id": 0,
                "source_id": 0,
                "embedding": 0,
                "sections": 1,
                "scope": 1,
                "score": {"$meta": "vectorSearchScore"},
            }
        },
    ]

    cursor = col.aggregate(pipeline)
    return await cursor.to_list(length=top_k)


def format_context(documents: list[dict]) -> str:
    if not documents:
        return "No relevant context found."

    parts = []
    for i, doc in enumerate(documents, 1):
        sections_text = "\n".join(doc.get("sections", []))
        parts.append(f"--- Document {i} (scope: {doc.get('scope', 'unknown')}) ---\n{sections_text}")

    return "\n\n".join(parts)
