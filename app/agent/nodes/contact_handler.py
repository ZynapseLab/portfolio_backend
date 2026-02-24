import logging

from langgraph.config import get_stream_writer

from app.agent.state import AgentState
from app.services.email_service import send_contact_email
from app.services.prompt_service import get_prompt
from app.services.translator import translate_text
from app.services.rate_limit_service import check_email_rate_limit
from app.utils.datetime_utils import utc_today

logger = logging.getLogger(__name__)


async def handle_contact(state: AgentState) -> dict:
    language = state.get("detected_language", "en")
    contact_data = state.get("contact_data", {})
    ip = state.get("ip", "unknown")
    date = utc_today()
    needs_translation = language.lower() not in ("en", "english")
    response_text = ""
    allowed, _ = await check_email_rate_limit(ip, date)

    writer = get_stream_writer()
    contact_result = ""
    
    if not allowed:
        response_text = get_prompt("contact_rate_limit")
    else:
        try:
            await send_contact_email(
                contact_data,
                ip,
                language="es" if needs_translation else "en",
            )
    
            contact_result = "email_sent"
            response_text = get_prompt("contact_confirmation")
        except Exception:
            contact_result = "email_failed"
            response_text = get_prompt("contact_error")
            logger.exception("Failed to send contact email")

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
