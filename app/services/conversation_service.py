import asyncio

from app.db.connection import get_connection


async def get_or_create_conversation(ip: str, scope: str, date: str) -> dict:
    def _query():
        conn = get_connection()
        row = conn.execute(
            "SELECT * FROM conversations "
            "WHERE ip=? AND scope=? AND date=? AND deleted=0",
            (ip, scope, date),
        ).fetchone()
        if row:
            return dict(row)
        cursor = conn.execute(
            "INSERT INTO conversations (ip, scope, date) VALUES (?, ?, ?)",
            (ip, scope, date),
        )
        conn.commit()
        return dict(
            conn.execute(
                "SELECT * FROM conversations WHERE id=?", (cursor.lastrowid,)
            ).fetchone()
        )

    return await asyncio.to_thread(_query)


async def append_message(conversation_id: int, role: str, content: str) -> None:
    def _insert():
        conn = get_connection()
        conn.execute(
            "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
            (conversation_id, role, content),
        )
        conn.commit()

    await asyncio.to_thread(_insert)


async def increment_messages_used(conversation_id: int) -> int:
    def _update():
        conn = get_connection()
        conn.execute(
            "UPDATE conversations SET messages_used = messages_used + 1 WHERE id=?",
            (conversation_id,),
        )
        conn.commit()
        row = conn.execute(
            "SELECT messages_used FROM conversations WHERE id=?",
            (conversation_id,),
        ).fetchone()
        return row["messages_used"]

    return await asyncio.to_thread(_update)


async def get_messages_used(ip: str, scope: str, date: str) -> int:
    def _query():
        conn = get_connection()
        row = conn.execute(
            "SELECT COALESCE(SUM(messages_used), 0) AS total "
            "FROM conversations WHERE ip=? AND scope=? AND date=?",
            (ip, scope, date),
        ).fetchone()
        return row["total"]

    return await asyncio.to_thread(_query)


async def soft_delete_conversation(ip: str, scope: str, date: str) -> bool:
    def _update():
        conn = get_connection()
        cursor = conn.execute(
            "UPDATE conversations SET deleted=1 "
            "WHERE ip=? AND scope=? AND date=? AND deleted=0",
            (ip, scope, date),
        )
        conn.commit()
        return cursor.rowcount > 0

    return await asyncio.to_thread(_update)


async def get_active_messages(ip: str, scope: str, date: str) -> list[dict]:
    def _query():
        conn = get_connection()
        row = conn.execute(
            "SELECT id FROM conversations "
            "WHERE ip=? AND scope=? AND date=? AND deleted=0",
            (ip, scope, date),
        ).fetchone()
        if not row:
            return []
        rows = conn.execute(
            "SELECT role, content FROM messages "
            "WHERE conversation_id=? ORDER BY id",
            (row["id"],),
        ).fetchall()
        return [dict(r) for r in rows]

    return await asyncio.to_thread(_query)


async def daily_cleanup(before_date: str) -> int:
    def _update():
        conn = get_connection()
        cursor = conn.execute(
            "UPDATE conversations SET deleted=1 WHERE date<? AND deleted=0",
            (before_date,),
        )
        conn.commit()
        return cursor.rowcount

    return await asyncio.to_thread(_update)
