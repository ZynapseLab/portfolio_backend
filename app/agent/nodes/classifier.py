import json

from app.agent.llm import classify_message
from app.agent.state import AgentState
from app.services.prompt_service import get_prompt

REQUIRED_CONTACT_FIELDS = {"name", "email", "subject", "message"}


async def classify(state: AgentState) -> dict:
    classifier_prompt = get_prompt("classifier_prompt")
    user_message = state["user_message"]

    conversation_history = state.get("conversation_history", [])
    raw = await classify_message(user_message, classifier_prompt, conversation_history)

    try:
        parsed = json.loads(raw)
        classification = parsed.get("classification", "OUT_OF_DOMAIN")
        language = parsed.get("language", "en")
        contact_data = parsed.get("contact_data", {})
    except (json.JSONDecodeError, AttributeError):
        classification = "OUT_OF_DOMAIN"
        language = "en"
        contact_data = {}

    valid = {"IN_DOMAIN", "OUT_OF_DOMAIN", "PROMPT_INJECTION", "CONTACT"}

    if classification not in valid:
        classification = "OUT_OF_DOMAIN"

    result: dict = {
        "classification": classification,
        "detected_language": language,
    }

    if classification == "CONTACT":
        provided = {k for k, v in contact_data.items() if v}
        missing = REQUIRED_CONTACT_FIELDS - provided

        if missing:
            result["classification"] = "CONTACT_INCOMPLETE"
            result["contact_data"] = contact_data
            result["missing_contact_fields"] = sorted(missing)
        else:
            result["contact_data"] = contact_data

    return result
