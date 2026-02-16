"""Endpoint DELETE /conversation."""
from fastapi import APIRouter, Request, Response, HTTPException
from app.auth.jwt import decode_jwt_token
from app.rate_limit.middleware import get_client_ip, get_utc_date
from app.database.collections import get_conversations_collection
from app.auth.cookies import delete_jwt_cookie


router = APIRouter()


@router.delete("/conversation")
async def delete_conversation_endpoint(
    request: Request,
    response: Response
):
    """
    Soft delete de conversación.
    NO reinicia el contador de mensajes.
    """
    # Obtener token de cookie
    token = request.cookies.get("session_token")
    
    if not token:
        raise HTTPException(status_code=401, detail="No hay sesión activa")
    
    # Decodificar token
    payload = decode_jwt_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    # Obtener datos del token
    ip = payload.get("ip")
    scope = payload.get("scope")
    date = payload.get("date")
    
    if not all([ip, scope, date]):
        raise HTTPException(status_code=400, detail="Token inválido")
    
    # Verificar que el IP del request coincida con el del token
    request_ip = get_client_ip(request)
    if ip != request_ip:
        raise HTTPException(status_code=403, detail="IP no coincide con la sesión")
    
    # Soft delete de la conversación
    collection = get_conversations_collection()
    result = await collection.update_one(
        {
            "ip": ip,
            "scope": scope,
            "date": date,
            "deleted": False
        },
        {
            "$set": {"deleted": True}
        }
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    
    # NO eliminar la cookie (el contador se mantiene)
    # Solo retornar éxito
    
    return {
        "message": "Conversación eliminada",
        "note": "El contador de mensajes se mantiene intacto"
    }
