from app.agent.llm import stream_chat_completion
from app.agent.state import AgentState
from app.services.prompt_service import get_prompt


async def reject(state: AgentState) -> dict:
    classification = state["classification"]
    language = state.get("detected_language", "en")

    if classification == "PROMPT_INJECTION": # TODO: Cambiar las respuestas para PI y OOD con mensajes predefinidos.
        template = get_prompt("prompt_injection_response")
    else:
        template = get_prompt("out_of_domain_response")

    if language.lower() not in ("en", "english"):
        translated = ""
        async for token in stream_chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": f"Translate the following text to {language}. "
                    "Output ONLY the translation, nothing else.",
                },
                {"role": "user", "content": template},
            ],
            temperature=0.3,
        ):
            translated += token
        response = translated
    else:
        response = template

    return {"full_response": response}
