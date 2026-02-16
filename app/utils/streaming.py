"""Utilidades para streaming NDJSON."""
import json
from typing import AsyncGenerator


async def stream_token(token: str) -> str:
    """Generar línea NDJSON para token."""
    return json.dumps({"type": "token", "data": token}) + "\n"


async def stream_done() -> str:
    """Generar línea NDJSON para fin de stream."""
    return json.dumps({"type": "done"}) + "\n"


async def stream_error(error: str) -> str:
    """Generar línea NDJSON para error."""
    return json.dumps({"type": "error", "data": error}) + "\n"
