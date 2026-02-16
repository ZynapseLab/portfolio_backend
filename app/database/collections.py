"""Definición de colecciones MongoDB."""
from app.database.connection import get_database


def get_knowledge_base_collection():
    """Colección knowledge_base para RAG."""
    return get_database()["knowledge_base"]


def get_conversations_collection():
    """Colección conversations para historial de chat."""
    return get_database()["conversations"]


def get_contact_leads_collection():
    """Colección contact_leads para formularios de contacto."""
    return get_database()["contact_leads"]


def get_prompts_collection():
    """Colección prompts para prompts del sistema."""
    return get_database()["prompts"]
