"""JWT manual para gestión de sesiones."""
import jwt
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
from app.config import settings


def create_jwt_token(
    ip: str,
    scope: str,
    messages_used: int,
    date: str
) -> str:
    """Crear token JWT."""
    payload = {
        "ip": ip,
        "scope": scope,
        "messages_used": messages_used,
        "date": date,
        "exp": datetime.now(timezone.utc) + timedelta(days=settings.jwt_expiration_days)
    }
    
    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )


def decode_jwt_token(token: str) -> Optional[Dict]:
    """Decodificar y validar token JWT."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_jwt_payload(token: str) -> Optional[Dict]:
    """Obtener payload sin validar expiración (para lectura)."""
    try:
        return jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            options={"verify_exp": False}
        )
    except jwt.InvalidTokenError:
        return None
