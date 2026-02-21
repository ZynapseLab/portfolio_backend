import json
import math

from app.agent.llm import get_openrouter_client
from app.db.connection import get_connection

_knowledge_cache: list[dict] | None = None


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def load_knowledge_cache() -> None:
    """Load all knowledge entries into memory for in-process vector search."""
    global _knowledge_cache
    conn = get_connection()
    rows = conn.execute(
        "SELECT scope, sections, embedding FROM knowledge_base"
    ).fetchall()
    _knowledge_cache = [
        {
            "scope": row["scope"],
            "sections": json.loads(row["sections"]),
            "embedding": json.loads(row["embedding"]),
        }
        for row in rows
    ]


async def generate_embedding(text: str) -> list[float]:
    client = get_openrouter_client()
    response = await client.embeddings.create(
        model="openai/text-embedding-3-small",
        input=text,
    )
    return response.data[0].embedding


async def vector_search(
    query_embedding: list[float],
    scope: str,
    top_k: int = 5,
) -> list[dict]:
    if _knowledge_cache is None:
        load_knowledge_cache()

    if scope == "global":
        candidates = [e for e in _knowledge_cache if e["scope"] in ("jonathan", "pablo")]
    else:
        candidates = [e for e in _knowledge_cache if e["scope"] == scope]

    scored = []
    for entry in candidates:
        score = _cosine_similarity(query_embedding, entry["embedding"])
        scored.append({
            "sections": entry["sections"],
            "scope": entry["scope"],
            "score": score,
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]


def format_context(documents: list[dict]) -> str:
    if not documents:
        return "No relevant context found."

    parts = []
    for i, doc in enumerate(documents, 1):
        sections_text = "\n".join(doc.get("sections", []))
        parts.append(
            f"--- Document {i} (scope: {doc.get('scope', 'unknown')}) ---\n{sections_text}"
        )

    return "\n\n".join(parts)
