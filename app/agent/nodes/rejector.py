from app.agent.llm import stream_chat_completion
from app.agent.state import AgentState
from app.services.prompt_service import get_prompt
from app.services.translator import translate_text


async def reject(state: AgentState) -> dict:
    classification = state["classification"]
    language = state.get("detected_language", "en")

    if (
        classification == "PROMPT_INJECTION"
    ):  # TODO: Cambiar las respuestas para PI y OOD con mensajes predefinidos.
        template = get_prompt("prompt_injection_response")
    else:
        template = get_prompt("out_of_domain_response")

    if language.lower() not in ("en", "english"):
        translated = translate_text(template, language)
    else:
        translated = template

    return {"full_response": translated}
