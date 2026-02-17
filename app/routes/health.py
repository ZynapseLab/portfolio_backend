from fastapi import APIRouter

from app.db.connection import get_database

router = APIRouter()


@router.get("/health")
async def health():
    db = get_database()
    await db.command("ping")
    return {"status": "ok"}
