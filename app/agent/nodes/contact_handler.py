from app.agent.llm import stream_chat_completion
from app.agent.state import AgentState
from app.services.prompt_service import get_prompt


async def handle_contact(state: AgentState) -> dict:
    language = state.get("detected_language", "en")
    confirmation = get_prompt("contact_confirmation")

    if language.lower() not in ("en", "english"):
        translated = ""
        async for token in stream_chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": f"Translate the following text to {language}. "
                    "Output ONLY the translation, nothing else.",
                },
                {"role": "user", "content": confirmation},
            ],
            temperature=0.3,
        ):
            translated += token
        response = translated
    else:
        response = confirmation

    return {
        "full_response": response,
        "contact_result": "contact_suggested",
    }
