from typing import AsyncGenerator

from langgraph.config import get_stream_writer

from app.agent.state import AgentState
from app.services.llm_service import translate_message
from app.services.prompt_service import get_prompt


async def _iter_template_tokens(template: str) -> AsyncGenerator:
    """
    Generator that yields tokens from the template string, with a space after each token.
    """
    for token in template:
        yield f"{token} "


async def reject(state: AgentState) -> dict:
    """
    Reject the user message and return a response based on the classification.
    If the classification is PROMPT_INJECTION, return the prompt injection response; otherwise, return the out-of-domain response.

    Args:
        state (AgentState): The current state of the agent, including the user message and classification.

    Returns:
        dict: A dictionary containing the full response to the user.
    """
    # Create the writer to stream tokens back to the client
    writer = get_stream_writer()

    # Get the classification and language from the state
    classification = state["classification"]
    language = state.get("detected_language", "en")

    # Determine the appropriate response template based on the classification
    template = (
        get_prompt("prompt_injection_response")
        if classification == "PROMPT_INJECTION"
        else get_prompt("out_of_domain_response")
    )

    # Determine if translation is needed
    needs_translation = language.lower() not in ("en", "english")

    # Stream tokens from the appropriate source (translation or template)
    full_response = ""
    token_stream = (
        translate_message(template, language)  # Stream translated tokens
        if needs_translation
        else _iter_template_tokens(template)  # Stream template tokens
    )

    async for token in token_stream:
        full_response += token
        writer({"type": "token", "data": token})
    writer({"type": "done"})

    return {"full_response": full_response if needs_translation else template}
