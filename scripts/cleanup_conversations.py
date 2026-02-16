"""Script de limpieza diaria de conversaciones."""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.connection import connect_to_mongo, close_mongo_connection
from app.database.collections import get_conversations_collection


async def cleanup_conversations(days_to_keep: int = 30):
    """
    Soft delete de conversaciones más antiguas que days_to_keep días.
    
    Args:
        days_to_keep: Número de días de conversaciones a mantener
    """
    print(f"🧹 Iniciando limpieza de conversaciones (manteniendo últimos {days_to_keep} días)...")
    
    # Conectar a MongoDB
    await connect_to_mongo()
    
    collection = get_conversations_collection()
    
    # Calcular fecha límite
    cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days_to_keep)).strftime("%Y-%m-%d")
    
    print(f"📅 Eliminando conversaciones anteriores a: {cutoff_date}")
    
    # Soft delete de conversaciones antiguas
    result = await collection.update_many(
        {
            "date": {"$lt": cutoff_date},
            "deleted": False
        },
        {
            "$set": {"deleted": True}
        }
    )
    
    print(f"✅ {result.modified_count} conversaciones marcadas como eliminadas")
    
    # Cerrar conexión
    await close_mongo_connection()
    
    print("✨ Limpieza completada!")


if __name__ == "__main__":
    # Por defecto, mantener 30 días
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    asyncio.run(cleanup_conversations(days))
