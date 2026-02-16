"""Conexión a MongoDB."""
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from typing import Optional


class MongoDB:
    """Cliente MongoDB singleton."""
    client: Optional[AsyncIOMotorClient] = None
    database = None


mongodb = MongoDB()


async def connect_to_mongo():
    """Conectar a MongoDB."""
    mongodb.client = AsyncIOMotorClient(settings.mongodb_uri)
    mongodb.database = mongodb.client[settings.mongodb_db_name]
    print(f"✅ Conectado a MongoDB: {settings.mongodb_db_name}")


async def close_mongo_connection():
    """Cerrar conexión a MongoDB."""
    if mongodb.client:
        mongodb.client.close()
        print("✅ Conexión a MongoDB cerrada")


def get_database():
    """Obtener instancia de la base de datos."""
    return mongodb.database
