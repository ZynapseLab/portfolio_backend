import json

from app.agent.state import AgentState
from app.services.llm_service import classify_user_message

REQUIRED_CONTACT_FIELDS = {"name", "email", "subject", "message"}
VALID_CLASSIFICATIONS = {"IN_DOMAIN", "OUT_OF_DOMAIN", "PROMPT_INJECTION", "CONTACT"}
VALID_SCOPES = {"jonathan", "pablo", "global"}


async def classify(state: AgentState) -> dict:
    # Get the conversation history and user message as input
    user_message = state["user_message"]
    conversation_history = state.get("conversation_history", [])

    # Classify the user message through the an LLM request
    raw = await classify_user_message(user_message, conversation_history)

    try:
        parsed = json.loads(raw)
        classification = parsed.get("classification", "OUT_OF_DOMAIN")
        language = parsed.get("language", "en")
        # contact_data = parsed.get("contact_data", {})
        resolved_scope = parsed.get("resolved_scope", "")
    except (json.JSONDecodeError, AttributeError):
        classification = "OUT_OF_DOMAIN"
        language = "en"
        # contact_data = {}
        resolved_scope = ""

    if classification not in VALID_CLASSIFICATIONS:
        classification = "OUT_OF_DOMAIN"

    # Override scope when the classifier narrows it from global.
    current_scope = state.get("scope", "global")

    if (
        current_scope == "global"
        and resolved_scope in VALID_SCOPES
        and resolved_scope != "global"
    ):
        current_scope = resolved_scope

    result = {
        "classification": classification,
        "detected_language": language,
        "scope": current_scope,
    }

    # if classification == "CONTACT":
    #     provided = {k for k, v in contact_data.items() if v}
    #     missing = REQUIRED_CONTACT_FIELDS - provided

    #     if missing:
    #         result["classification"] = "CONTACT_INCOMPLETE"
    #         result["contact_data"] = contact_data
    #         result["missing_contact_fields"] = sorted(missing)
    #     else:
    #         result["contact_data"] = contact_data

    return result
