from app.agent.llm import get_openrouter_client
from app.config import settings


async def translate_text(text: str, target_language: str) -> str:
    """
    Translates text from English to the target language using OpenRouter.

    Args:
        text: The text to translate.
        target_language: The target language to translate to.

    Returns:
        The translated text.
    """
    client = get_openrouter_client()

    stream = await client.chat.completions.create(
        model=settings.OPENROUTER_TRANSLATOR_MODEL,
        messages=[
            {
                "role": "user",
                "content": f"Translate the following text from English to {target_language}. "
                "Return ONLY the translated text, nothing else.\n\n"
                f"{text}",
            }
        ],
        temperature=0.3,
        stream=True,
    )

    async for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            yield delta.content
