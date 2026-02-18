from collections.abc import AsyncGenerator

from openai import AsyncOpenAI

from app.config import settings

_openrouter_client: AsyncOpenAI | None = None


def get_openrouter_client() -> AsyncOpenAI:
    global _openrouter_client

    if _openrouter_client is None:
        _openrouter_client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.OPENROUTER_API_KEY,
        )

    return _openrouter_client


async def stream_chat_completion(
    messages: list[dict],
    model: str | None = None,
    temperature: float = 0.7,
) -> AsyncGenerator[str, None]:
    client = get_openrouter_client()
    model = model or settings.OPENROUTER_MODEL

    stream = await client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        stream=True,
    )

    async for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            yield delta.content


async def classify_message(user_message: str, classifier_prompt: str) -> str:
    client = get_openrouter_client()
    prompt = classifier_prompt.replace("{user_message}", user_message)

    response = await client.chat.completions.create(
        model=settings.OPENROUTER_CLASSIFIER_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
    )

    return response.choices[0].message.content or ""
