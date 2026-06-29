from abc import ABC, abstractmethod
from typing import Optional


class BaseVectorizer(ABC):
    def __init__(self, model_name: str, dimension: Optional[int] = None) -> None:
        self.model_name = model_name
        self.dimension = dimension

    @abstractmethod
    async def vectorize(self, text: str) -> list:
        """
        Abstract method to vectorize a given text.
        """
        raise NotImplementedError

    @abstractmethod
    async def vectorize_many(self, texts: list) -> list:
        """
        Abstract method to vectorize a batch of texts.
        """
        raise NotImplementedError
