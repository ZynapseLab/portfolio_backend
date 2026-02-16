"""Middleware de rate limiting."""
from fastapi import Request, HTTPException, status
from datetime import datetime, timezone, timedelta
from typing import Optional
from app.auth.jwt import decode_jwt_token, create_jwt_token
from app.rate_limit.models import RateLimitInfo
from app.config import settings
from app.models.chat import RateLimitError


def get_client_ip(request: Request) -> str:
    """Obtener IP del cliente."""
    # Verificar headers de proxy
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def get_utc_date() -> str:
    """Obtener fecha UTC en formato YYYY-MM-DD."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def get_reset_time() -> datetime:
    """Obtener tiempo de reset (medianoche UTC del día siguiente)."""
    now = datetime.now(timezone.utc)
    tomorrow = now + timedelta(days=1)
    return tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)


async def check_rate_limit(
    request: Request,
    scope: str,
    limit_type: str = "chat"  # "chat" o "email"
) -> RateLimitInfo:
    """Verificar rate limit y retornar información."""
    ip = get_client_ip(request)
    date = get_utc_date()
    
    # Obtener token de cookie
    token = request.cookies.get("session_token")
    payload = None
    
    if token:
        payload = decode_jwt_token(token)
    
    # Si el token es válido y corresponde a este IP/scope/date, usar sus datos
    if payload and payload.get("ip") == ip and payload.get("scope") == scope and payload.get("date") == date:
        messages_used = payload.get("messages_used", 0)
    else:
        messages_used = 0
    
    # Determinar límite según tipo
    limit = settings.rate_limit_chat_messages if limit_type == "chat" else settings.rate_limit_emails
    
    # Verificar si excede el límite
    if messages_used >= limit:
        reset_at = get_reset_time()
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=RateLimitError(
                type="rate_limit",
                limit=limit,
                used=messages_used,
                reset_at=reset_at.isoformat()
            ).model_dump()
        )
    
    return RateLimitInfo(
        used=messages_used,
        limit=limit,
        reset_at=get_reset_time()
    )


def increment_rate_limit(
    ip: str,
    scope: str,
    current_used: int,
    limit_type: str = "chat"
) -> tuple[str, int]:
    """Incrementar contador de rate limit y retornar nuevo token."""
    date = get_utc_date()
    new_used = current_used + 1
    
    token = create_jwt_token(
        ip=ip,
        scope=scope,
        messages_used=new_used,
        date=date
    )
    
    return token, new_used
