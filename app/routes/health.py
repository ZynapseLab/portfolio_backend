from fastapi import APIRouter

from app.db.connection import get_connection

router = APIRouter()


@router.get("/health")
async def health():
    conn = get_connection()
    conn.execute("SELECT 1")
    return {"status": "ok"}
