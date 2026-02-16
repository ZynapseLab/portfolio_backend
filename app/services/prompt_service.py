"""Servicio seguro de gestión de prompts."""
from app.database.collections import get_prompts_collection
from typing import Optional, Dict


async def get_prompt(prompt_name: str) -> Optional[str]:
    """Obtener prompt del sistema de forma segura."""
    collection = get_prompts_collection()
    doc = await collection.find_one({"name": prompt_name})
    
    if doc:
        return doc.get("content")
    return None


async def set_prompt(prompt_name: str, content: str):
    """Establecer prompt del sistema."""
    collection = get_prompts_collection()
    await collection.update_one(
        {"name": prompt_name},
        {"$set": {"content": content, "name": prompt_name}},
        upsert=True
    )


async def get_system_prompts() -> Dict[str, str]:
    """Obtener todos los prompts del sistema."""
    collection = get_prompts_collection()
    cursor = collection.find({})
    prompts = {}
    
    async for doc in cursor:
        prompts[doc["name"]] = doc.get("content", "")
    
    return prompts
