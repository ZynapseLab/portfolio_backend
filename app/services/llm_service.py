import re
from collections.abc import AsyncGenerator

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam

from app.config import settings
from app.services.prompt_service import get_prompt

_openrouter_client: AsyncOpenAI | None = None


def get_openrouter_client() -> AsyncOpenAI:
    """
    Returns the OpenRouter client, initializing it if necessary.
    """
    global _openrouter_client

    if _openrouter_client is None:
        _openrouter_client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.OPENROUTER_API_KEY,
        )

    return _openrouter_client


def _chat_completion_kwargs(
    messages: list[ChatCompletionMessageParam],
    model: str | None = None,
    temperature: float = 0.8,
    top_p: float = 0.85,
    max_tokens: int | None = None,
) -> dict:
    return {
        "messages": messages,
        "model": model or settings.OPENROUTER_MODEL,
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens,
    }


async def complete_chat(
    messages: list[ChatCompletionMessageParam],
    model: str | None = None,
    temperature: float = 0.8,
    top_p: float = 0.85,
    max_tokens: int | None = None,
) -> str:
    """
    Returns a full chat completion response using the OpenRouter client.

    Args:
        messages: The list of message dictionaries to send to the model.
        model: The model to use for the chat completion. If None, uses the default model from settings.
        temperature: The temperature to use for the chat completion.
        top_p: The top-p value to use for the chat completion.
        max_tokens: The maximum number of tokens to generate in the response. If None, uses the default from the model.

    Returns:
        The completed response text.
    """
    client = get_openrouter_client()

    response = await client.chat.completions.create(
        **_chat_completion_kwargs(messages, model, temperature, top_p, max_tokens),
        stream=False,
    )

    return response.choices[0].message.content or ""


async def stream_chat_completion(
    messages: list[ChatCompletionMessageParam],
    model: str | None = None,
    temperature: float = 0.8,
    top_p: float = 0.85,
    max_tokens: int | None = None,
) -> AsyncGenerator[str, None]:
    """
    Streams a chat completion using the OpenRouter client.

    Args:
        messages: The list of message dictionaries to send to the model.
        model: The model to use for the chat completion. If None, uses the default model from settings.
        temperature: The temperature to use for the chat completion.
        top_p: The top-p value to use for the chat completion.
        max_tokens: The maximum number of tokens to generate in the response. If None, uses the default from the model.

    Yields:
        The content of each chunk in the chat completion stream.
    """
    client = get_openrouter_client()

    stream = await client.chat.completions.create(
        **_chat_completion_kwargs(messages, model, temperature, top_p, max_tokens),
        stream=True,
    )

    async for chunk in stream:
        if not chunk.choices:
            continue

        delta = chunk.choices[0].delta
        if delta.content:
            yield delta.content


async def classify_user_message(
    user_message: str,
    conversation_history: list[ChatCompletionMessageParam] | None = None,
) -> str:
    """
    Classifies a user message using the OpenRouter chat completion API.

    Args:
        user_message (str): The message to classify.
        classifier_prompt (str): The prompt to use for classification.
        conversation_history (list[dict] | None): The conversation history to use for context.

    Returns:
        str: The classification result.
    """
    client = get_openrouter_client()

    # Get the classifier prompt and replace the user message placeholder.
    prompt = get_prompt("classifier")
    prompt = prompt.replace("{user_message}", user_message)

    messages: list[ChatCompletionMessageParam] = [
        {
            "role": "system",
            "content": prompt,
        },
    ]

    # Extends the messages list with the conversation history, if provided.
    if conversation_history:
        messages.extend(conversation_history)

    # Appends the user message to the messages list.
    messages.append({"role": "user", "content": user_message})

    # Sends the messages to the OpenRouter API and returns the classification result.
    response = await client.chat.completions.create(
        messages=messages,
        model=settings.OPENROUTER_CLASSIFIER_MODEL,
        temperature=0.0,
    )

    return response.choices[0].message.content or ""


async def translate_message(
    text: str,
    target_language: str,
) -> AsyncGenerator[str, None]:
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
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta
        if delta.content:
            yield delta.content
