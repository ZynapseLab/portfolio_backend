from langgraph.config import get_stream_writer

from app.agent.state import AgentState
from app.services.prompt_service import get_prompt
from app.services.translator import translate_text


async def handle_contact(state: AgentState) -> dict:
    language = state.get("detected_language", "en")
    confirmation = get_prompt("contact_confirmation")
    writer = get_stream_writer()

    needs_translation = language.lower() not in ("en", "english")
    translated = ""

    if needs_translation:
        async for token in translate_text(confirmation, language):
            translated += token
            writer({"type": "token", "data": token})
    else:
        async for token in confirmation:
            writer({"type": "token", "data": f"{token} "})

    writer({"type": "done"})

    return {
        "full_response": translated if needs_translation else confirmation,
        "contact_result": "contact_suggested",
    }
