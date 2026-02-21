from typing import TypedDict


class AgentState(TypedDict, total=False):
    # Input
    user_message: str
    scope: str
    conversation_history: list[dict]
    ip: str

    # Classification
    classification: str
    detected_language: str

    # RAG
    retrieved_context: str

    # Generation
    full_response: str
    _messages: list[dict]

    # Contact
    contact_data: dict
    contact_result: str
