from app.config import settings
from app.services.llm_service import complete_chat


async def parse_query(query: str) -> str:
    PROMPT = f"""
    You are a Query Parsing module for a RAG assistant system.

    Your task is to analyze the user's query and convert it into a structured representation that helps the retrieval system find relevant information in a document collection.

    Do not answer the user's question.
    Do not invent information.

    Goal:
    Extract the user's intent, key search terms, entities, filters, and an optimized retrieval query.

    User query:
    {query}
    """

    parsed_query = await complete_chat(
        messages=[
            {
                "role": "user",
                "content": PROMPT,
            }
        ],
        model=settings.OPENROUTER_MODEL,
        temperature=0.6,
        top_p=0.7,
    )

    return parsed_query
