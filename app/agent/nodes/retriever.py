from app.agent.state import AgentState
from app.services.knowledge_service import (
    format_context,
    generate_embedding,
    vector_search,
)


async def retrieve(state: AgentState) -> dict:
    user_message = state["user_message"]
    scope = state["scope"]

    embedding = await generate_embedding(user_message)
    documents = await vector_search(embedding, scope)
    context = format_context(documents)

    return {"retrieved_context": context}
