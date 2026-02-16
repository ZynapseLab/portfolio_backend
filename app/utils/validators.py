"""Validadores de datos."""
import re
from typing import Optional


def validate_scope(scope: str) -> bool:
    """Validar que el scope sea válido."""
    return scope in ["global", "jonathan", "pablo"]


def sanitize_message(message: str) -> str:
    """Sanitizar mensaje de usuario."""
    # Eliminar caracteres de control excepto espacios y saltos de línea
    message = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', message)
    # Limitar longitud
    return message[:2000].strip()
