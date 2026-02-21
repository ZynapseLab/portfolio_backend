from app.db.connection import get_connection

_cache: dict[str, str] = {}


def load_prompts() -> None:
    global _cache
    conn = get_connection()
    rows = conn.execute("SELECT key, content FROM prompts").fetchall()
    _cache = {row["key"]: row["content"] for row in rows}


def get_prompt(key: str) -> str:
    if key not in _cache:
        raise KeyError(f"Prompt '{key}' not found in cache. Run load_prompts() first.")
    return _cache[key]
