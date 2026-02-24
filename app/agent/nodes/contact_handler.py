import logging

from langgraph.config import get_stream_writer

from app.agent.state import AgentState
from app.services.email_service import send_contact_email
from app.services.prompt_service import get_prompt
from app.services.translator import translate_text

logger = logging.getLogger(__name__)


async def handle_contact(state: AgentState) -> dict:
    language = state.get("detected_language", "en")
    writer = get_stream_writer()

    contact_data = state.get("contact_data", {})
    ip = state.get("ip", "unknown")
    needs_translation = language.lower() not in ("en", "english")

    try:
        await send_contact_email(contact_data, ip, language = "es" if needs_translation else "en") 
        contact_result = "email_sent"
        response_text = get_prompt("contact_confirmation")
    except Exception:
        logger.exception("Failed to send contact email")
        contact_result = "email_failed"
        response_text = get_prompt("contact_error")

    translated = ""

    if needs_translation:
        async for token in translate_text(response_text, language):
            translated += token
            writer({"type": "token", "data": token})
    else:
        async for token in response_text:
            writer({"type": "token", "data": f"{token} "})

    writer({"type": "done"})

    return {
        "full_response": translated if needs_translation else response_text,
        "contact_result": contact_result,
    }
