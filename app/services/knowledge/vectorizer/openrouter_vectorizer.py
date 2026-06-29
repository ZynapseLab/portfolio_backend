from typing import Optional

from openai import AsyncOpenAI

from .base_vectorizer import BaseVectorizer


class OpenRouterVectorizer(BaseVectorizer):
    def __init__(
        self, client: AsyncOpenAI, model_name: str, dimension: Optional[int] = None
    ):
        super().__init__(model_name, dimension)
        self._client = client

    async def vectorize(self, text: str) -> list[float]:
        response = await self._client.embeddings.create(
            model=self.model_name,
            input=text,
        )

        return response.data[0].embedding

    async def vectorize_many(self, texts: list[str]) -> list[list[float]]:
        response = await self._client.embeddings.create(
            model=self.model_name,
            input=texts,
        )

        return [r.embedding for r in response.data]
