from weaviate.classes.query import MetadataQuery
from weaviate.collections.classes.filters import Filter

from app.agent.llm import get_openrouter_client
from app.services.vector_store_service import weaviate_client_manager
from app.services.vector_store_service.schemas import KNOWLEDGE_COLLECTIONS


def load_knowledge_cache() -> None:
    """Kept for startup compatibility; Weaviate serves knowledge at query time."""


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
    top_k: int = 10,
) -> list[dict]:
    collection_name = KNOWLEDGE_COLLECTIONS["devs"]
    filters = None if scope == "global" else Filter.by_property("scope").equal(scope)

    async with weaviate_client_manager as client:
        if not await client.collections.exists(collection_name):
            return []

        collection = client.collections.get(collection_name)
        response = await collection.query.near_vector(
            near_vector=query_embedding,
            limit=top_k,
            filters=filters,
            return_metadata=MetadataQuery(distance=True),
            return_properties=["scope", "section_text"],
        )

    return [
        {
            "sections": [obj.properties["section_text"]],
            "scope": obj.properties["scope"],
            "score": 1 - obj.metadata.distance
            if obj.metadata and obj.metadata.distance is not None
            else 0.0,
        }
        for obj in response.objects
    ]


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
