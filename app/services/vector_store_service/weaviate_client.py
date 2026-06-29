from typing import Any

import weaviate
from weaviate.classes.init import Auth
from weaviate.client import WeaviateAsyncClient
from weaviate.collections.classes.config import Configure

from app.config import settings

from .schemas import WEAVIATE_COLLECTION_SCHEMAS


class WeaviateClientManager:
    def __init__(self, url, api_key) -> None:
        self._url = url
        self._api_key = api_key

        self._client: WeaviateAsyncClient | None = None

    async def __aenter__(self) -> WeaviateAsyncClient:
        """
        Connects to the Weaviate client and returns it.

        Raises:
            RuntimeError: If the client is not ready after connecting.
        """
        try:
            if not self._url:
                raise RuntimeError("WEAVIATE_URL is required for Weaviate Cloud")
            if not self._api_key:
                raise RuntimeError("WEAVIATE_API_KEY is required for Weaviate Cloud")

            # Create the Weaviate client instance
            self._client = weaviate.use_async_with_weaviate_cloud(
                cluster_url=self._url,
                auth_credentials=Auth.api_key(self._api_key),
                skip_init_checks=True,
            )

            # Connect to the client
            await self._client.connect()

            # Ensure the client is ready
            if not await self._client.is_ready():
                raise RuntimeError("Client is not ready")

            return self._client
        except Exception as e:
            if self._client is not None:
                await self._client.close()
                self._client = None
            raise RuntimeError(
                "Failed to connect to Weaviate Cloud. "
                "Check WEAVIATE_URL and WEAVIATE_API_KEY. "
                f"Original error: {e}"
            ) from e

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Closes the Weaviate client connection.
        """
        if self._client is not None:
            await self._client.close()

        self._client = None

    async def ensure_collection(self, collection_name: str) -> None:
        """
        Ensures that the specified collection exists in the Weaviate client.

        Raises:
            RuntimeError: If the client is not connected or the collection creation fails.
            ValueError: If the collection name is unknown.
        """
        try:
            if self._client is None:
                raise RuntimeError("Client is not connected")

            if collection_name not in WEAVIATE_COLLECTION_SCHEMAS:
                raise ValueError(f"Unknown collection: {collection_name}")

            if await self._client.collections.exists(collection_name):
                return

            await self._client.collections.create(
                collection_name,
                properties=WEAVIATE_COLLECTION_SCHEMAS[collection_name],
                vector_config=Configure.Vectors.self_provided(),
            )
        except Exception as e:
            raise RuntimeError(f"Failed to ensure collection {collection_name}: {e}")

    async def load_existing(
        self, collection: Any, include_vector: bool = False
    ) -> dict[str, dict]:
        """
        Loads existing knowledge chunks from the Weaviate collection.

        Returns:
            dict[str, dict]: A dictionary mapping source IDs to their properties.
        """
        existing = {}
        after = None

        while True:
            response = await collection.query.fetch_objects(
                limit=1000,
                after=after,
                include_vector=include_vector,
                return_properties=["source_id", "content_hash", "embedding_model"],
            )

            if not response.objects:
                break

            for obj in response.objects:
                source_id = obj.properties["source_id"]
                if include_vector:
                    existing[source_id] = {
                        "properties": obj.properties,
                        "vector": obj.vector,
                    }
                else:
                    existing[source_id] = obj.properties

            after = response.objects[-1].uuid

        return existing


weaviate_client_manager = WeaviateClientManager(
    url=settings.WEAVIATE_URL,
    api_key=settings.WEAVIATE_API_KEY,
)
