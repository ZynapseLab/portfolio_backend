from typing import TypedDict

from openai.types.chat import ChatCompletionMessageParam


class AgentState(TypedDict):
    # Input
    user_message: str
    scope: str
    conversation_history: list[ChatCompletionMessageParam]
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
    missing_contact_fields: list[str]
