from langgraph.config import get_stream_writer

from app.agent.state import AgentState
from app.services.prompt_service import get_prompt
from app.services.translator import translate_text


async def reject(state: AgentState) -> dict:
    classification = state["classification"]
    language = state.get("detected_language", "en")
    writer = get_stream_writer()

    if (
        classification == "PROMPT_INJECTION"
    ):  # TODO: Cambiar las respuestas para PI y OOD con mensajes predefinidos.
        template = get_prompt("prompt_injection_response")
    else:
        template = get_prompt("out_of_domain_response")

    if language.lower() not in ("en", "english"):
        translated = ""
        async for token in translate_text(template, language):
            translated += token
            writer({"type": "token", "data": token})
    else:
        async for token in template:
            writer({"type": "token", "data": token})

    return {"full_response": translated}
