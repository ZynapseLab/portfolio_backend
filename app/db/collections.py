from motor.motor_asyncio import AsyncIOMotorCollection

from app.db.connection import get_database


def conversations_col() -> AsyncIOMotorCollection:
    return get_database()["conversations"]


def prompts_col() -> AsyncIOMotorCollection:
    return get_database()["prompts"]


def knowledge_base_col() -> AsyncIOMotorCollection:
    return get_database()["knowledge_base"]


def contact_leads_col() -> AsyncIOMotorCollection:
    return get_database()["contact_leads"]
