from app.db.collections import prompts_col

_cache: dict[str, str] = {}


async def load_prompts() -> None:
    global _cache
    col = prompts_col()
    cursor = col.find({}, {"key": 1, "content": 1, "_id": 0})
    docs = await cursor.to_list(length=100)
    _cache = {doc["key"]: doc["content"] for doc in docs}


def get_prompt(key: str) -> str:
    if key not in _cache:
        raise KeyError(f"Prompt '{key}' not found in cache. Run load_prompts() first.")
    return _cache[key]
