"""Endpoint para formulario de contacto."""
from fastapi import APIRouter, Request, HTTPException
from app.models.contact import ContactRequest
from app.services.email_service import send_email
from app.rate_limit.middleware import (
    check_rate_limit,
    get_client_ip,
    increment_rate_limit
)
from app.auth.jwt import decode_jwt_token


router = APIRouter()


@router.post("/contact")
async def contact_endpoint(
    request: Request,
    contact_request: ContactRequest
):
    """
    Endpoint para enviar formulario de contacto.
    Rate limit: 2 emails por día por IP.
    """
    ip = get_client_ip(request)
    
    # Verificar rate limit para emails
    try:
        await check_rate_limit(
            request,
            scope="contact",  # Scope especial para contactos
            limit_type="email"
        )
    except HTTPException as e:
        if e.status_code == 429:
            raise e
    
    # Obtener token actual para incrementar contador
    token = request.cookies.get("session_token")
    current_used = 0
    
    if token:
        payload = decode_jwt_token(token)
        if payload:
            current_used = payload.get("messages_used", 0)
    
    # Incrementar rate limit
    increment_rate_limit(
        ip,
        "contact",
        current_used,
        limit_type="email"
    )
    
    # Enviar email con retries
    success = await send_email(contact_request)
    
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Error al enviar el correo. Por favor intenta más tarde."
        )
    
    return {
        "message": "Correo enviado exitosamente",
        "status": "success"
    }
