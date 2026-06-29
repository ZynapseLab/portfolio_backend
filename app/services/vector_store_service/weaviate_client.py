import weaviate
from weaviate.classes.init import Auth
from weaviate.client import WeaviateAsyncClient

from app.config import settings


class WeaviateClientManager:
    def __init__(self, host, port, grpc_port, api_key) -> None:
        self._host = host
        self._port = port
        self._grpc_port = grpc_port
        self._api_key = api_key

        self._client: WeaviateAsyncClient | None = None

    async def __aenter__(self) -> WeaviateAsyncClient:
        self._client = weaviate.use_async_with_local(
            host=self._host,
            port=self._port,
            grpc_port=self._grpc_port,
            auth_credentials=Auth.api_key(self._api_key),
        )

        await self._client.connect()

        if not await self._client.is_ready():
            raise RuntimeError("Client is not ready")

        return self._client

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._client is not None:
            await self._client.close()

        self._client = None


weaviate_client_manager = WeaviateClientManager(
    host=settings.WEAVIATE_HOST,
    port=settings.WEAVIATE_PORT,
    grpc_port=settings.WEAVIATE_GRPC_PORT,
    api_key=settings.WEAVIATE_API_KEY,
)
