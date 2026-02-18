import json

from app.agent.llm import classify_message
from app.agent.state import AgentState
from app.services.prompt_service import get_prompt


async def classify(state: AgentState) -> dict:
    classifier_prompt = get_prompt("classifier_prompt")
    user_message = state["user_message"]

    raw = await classify_message(user_message, classifier_prompt)

    try:
        parsed = json.loads(raw)
        classification = parsed.get("classification", "OUT_OF_DOMAIN")
        language = parsed.get("language", "en")
    except (json.JSONDecodeError, AttributeError):
        classification = "OUT_OF_DOMAIN"
        language = "en"

    valid = {"IN_DOMAIN", "OUT_OF_DOMAIN", "PROMPT_INJECTION", "CONTACT"}
    
    if classification not in valid:
        classification = "OUT_OF_DOMAIN"

    return {
        "classification": classification,
        "detected_language": language,
    }
