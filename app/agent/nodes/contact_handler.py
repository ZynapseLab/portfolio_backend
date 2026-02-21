from app.agent.llm import stream_chat_completion
from app.agent.state import AgentState
from app.services.prompt_service import get_prompt
from app.services.translator import translate_text


async def handle_contact(state: AgentState) -> dict:
    language = state.get("detected_language", "en")
    confirmation = get_prompt("contact_confirmation")

    if language.lower() not in ("en", "english"):
        translated = await translate_text(confirmation, language)
        response = translated
    else:
        response = confirmation

    return {
        "full_response": response,
        "contact_result": "contact_suggested",
    }
