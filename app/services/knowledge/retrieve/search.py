from typing import Optional

from openai.types.chat import ChatCompletionMessageParam
from weaviate.classes.query import MetadataQuery
from weaviate.collections.classes.filters import Filter
from weaviate.collections.classes.grpc import HybridFusion

from app.config import settings
from app.services.knowledge.vectorizer import OpenRouterVectorizer
from app.services.llm_service import complete_chat, get_openrouter_client
from app.services.prompt_service import get_prompt
from app.services.vector_store_service import weaviate_client_manager
from app.services.vector_store_service.schemas import KNOWLEDGE_COLLECTIONS

_query_vectorizer = OpenRouterVectorizer(
    client=get_openrouter_client(),
    model_name=settings.OPENROUTER_EMBEDDING_MODEL,
)

HYBRID_ALPHA = 0.65
HYBRID_QUERY_PROPERTIES = [
    "section_heading^3",
    "section_text",
    "embed_text",
]
RETURN_PROPERTIES = [
    "source_id",
    "scope",
    "source_heading",
    "section_heading",
    "chunk_index",
    "section_text",
]


async def classify_retrieval_process(query: str) -> str:
    """
    Classifies the user's query into one of the two categories: devs or projects.

    Returns the category name as a string.

    Example:
        query = "What are the developer's skills?"
        return = "devs"

    Args:
        query (str): The user's query to classify.

    Returns:
        str: The category name ("devs" or "projects").
    """

    PROMPT = f"""
    You are a classifier agent for the retrieval step of a RAG system.

    Your task is to classify the user's query into exactly one of these categories:

    - devs: Questions about the developers, their profiles, experience, skills, background, education, work history, technologies, availability, contact information, or professional trajectory.
    - projects: Questions about portfolio projects, products, applications, technical implementations, repositories, features, architecture, stack used in a project, project results, or project-specific details.

    Return only the category name:
    devs
    or
    projects

    Do not explain your reasoning. Do not add extra text.

    Classification rules:
    - If the query asks about a person, developer, engineer, skill set, career, experience, role, resume, biography, or contact details, classify it as devs.
    - If the query asks about something built, shipped, implemented, designed, deployed, or shown in the portfolio, classify it as projects.
    - If the query mentions both a developer and a project, classify based on the main intent of the question.
    - If the user asks who made a project or what a developer did inside a project, classify it as projects because the target context is project-specific.
    - If the query is ambiguous but seems to ask about capabilities or background, classify it as devs.
    - If the query is ambiguous but seems to ask about work samples, apps, demos, or repositories, classify it as projects.

    Examples:

    Query: "What technologies does Pablo work with?"
    Classification: devs

    Query: "Tell me about Jonathan's professional experience."
    Classification: devs

    Query: "Does Pablo have backend experience?"
    Classification: devs

    Query: "How can I contact Jonathan?"
    Classification: devs

    Query: "What projects are included in the portfolio?"
    Classification: projects

    Query: "How was the chatbot implemented?"
    Classification: projects

    Query: "Which project uses FastAPI and LangGraph?"
    Classification: projects

    Query: "What features does the portfolio app have?"
    Classification: projects

    QUERY:
    {query}
    """

    llm_response = await complete_chat(
        messages=[
            {
                "role": "user",
                "content": PROMPT,
            }
        ],
        model=settings.OPENROUTER_CLASSIFIER_MODEL,
        temperature=0.0,
        max_tokens=1,
    )

    return llm_response


async def retireve(
    query: str,
    top_k: int,
    retrieval_classification: str,
    query_scope: Optional[str] = None,
) -> list[dict]:
    """
    Retrieves documents from the knowledge base based on the user's query and classification.

    Args:
        query (str): The user's query to retrieve documents for.
        top_k (int): The number of top documents to retrieve.
        retrieval_classification (str): The classification of the query (devs or projects).
        query_scope (Optional[str]): The scope of the query (optional).

    Returns:
        list[dict]: A list of retrieved documents as dictionaries.
    """
    if retrieval_classification not in KNOWLEDGE_COLLECTIONS:
        raise ValueError(
            f"Unknown retrieval classification: {retrieval_classification}"
        )

    # Retrieve the collection name based on the classification
    coll_name = KNOWLEDGE_COLLECTIONS[retrieval_classification]
    # Set the limit and filters for the query
    limit = max(1, top_k)
    filters = None

    # Apply query scope filter if request ask for devs information
    if query_scope and query_scope != "global":
        filters = Filter.by_property("scope").equal(query_scope)

    async with weaviate_client_manager as client:
        # Handle collection not found case
        if not await client.collections.exists(coll_name):
            return []

        # Get the collection and vectorize the query
        coll = client.collections.use(coll_name)
        query_vector = await _query_vectorizer.vectorize(query)

        # Perform hybrid search
        results = await coll.query.hybrid(
            query=query,
            vector=query_vector,
            alpha=HYBRID_ALPHA,
            limit=limit,
            filters=filters,
            fusion_type=HybridFusion.RELATIVE_SCORE,
            query_properties=HYBRID_QUERY_PROPERTIES,
            return_metadata=MetadataQuery(score=True, explain_score=True),
            return_properties=RETURN_PROPERTIES,
        )

        # Handle no results case
        if not results.objects:
            return []

        # Return results
        return [
            {
                "source_id": obj.properties.get("source_id"),
                "scope": obj.properties.get("scope"),
                "source_heading": obj.properties.get("source_heading"),
                "section_heading": obj.properties.get("section_heading"),
                "chunk_index": obj.properties.get("chunk_index"),
                "section_text": obj.properties.get("section_text"),
                "score": obj.metadata.score if obj.metadata else None,
                "explain_score": obj.metadata.explain_score if obj.metadata else None,
            }
            for obj in results.objects
        ]


def augment_query(
    query: str,
    documents: list[dict],
    messages: list[ChatCompletionMessageParam],
    max_messages: int = 6,
) -> str:
    """
    Augments the user's query with retrieved documents and conversation history.

    Args:
        query (str): The user's query to augment.
        documents (list[str]): The retrieved documents to include in the augmented query.
        messages (list[dict]): The conversation history to include in the augmented query.

    Returns:
        str: The augmented query string.
    """
    system_prompt = get_prompt("")

    recent_messages = (
        messages[-max_messages:] if len(messages) > max_messages else messages
    )

    AUGMENTED_QUERY = f"""
    # System Instructions
    {system_prompt}

    {"# Conversation History\n" if len(messages) > 0 else ""}
    {"".join([f"{message['role']}: {message['content']}\n" for message in recent_messages])}

    {"# Retrieved Documents\n" if len(documents) > 0 else ""}
    {"".join([f"[DOC{idx}]\nContent: {doc['section_text']}\n" for idx, doc in enumerate(documents)])}

    # Current Query
    {query}
    """

    return AUGMENTED_QUERY
