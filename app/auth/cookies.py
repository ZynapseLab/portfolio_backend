"""Gestión de cookies httpOnly."""
from fastapi import Response
from datetime import timedelta
from app.config import settings


def set_jwt_cookie(response: Response, token: str):
    """Establecer cookie httpOnly con JWT."""
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        secure=not settings.debug,  # Solo HTTPS en producción
        samesite="lax",
        max_age=settings.jwt_expiration_days * 24 * 60 * 60  # Segundos
    )


def delete_jwt_cookie(response: Response):
    """Eliminar cookie JWT."""
    response.set_cookie(
        key="session_token",
        value="",
        httponly=True,
        secure=not settings.debug,
        samesite="lax",
        max_age=0
    )
