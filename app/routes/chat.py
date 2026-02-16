"""Endpoint /chat."""
import time
import uuid
from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import StreamingResponse
from app.models.chat import ChatRequest
from app.rate_limit.middleware import (
    check_rate_limit,
    get_client_ip,
    get_utc_date,
    increment_rate_limit
)
from app.auth.jwt import decode_jwt_token
from app.auth.cookies import set_jwt_cookie
from app.agents.langgraph_agent import process_chat_message
from app.utils.streaming import stream_token, stream_done, stream_error
from app.logging.logger import log_request, hash_ip
from app.database.collections import get_conversations_collection
from app.models.conversation import Message
from datetime import datetime
from app.utils.validators import sanitize_message


router = APIRouter()


@router.post("/chat")
async def chat_endpoint(
    request: Request,
    chat_request: ChatRequest,
    response: Response
):
    """
    Endpoint principal de chat con streaming NDJSON.
    """
    start_time = time.time()
    request_id = str(uuid.uuid4())
    ip = get_client_ip(request)
    ip_hash = hash_ip(ip)
    
    try:
        # Sanitizar mensaje
        sanitized_message = sanitize_message(chat_request.message)
        if not sanitized_message:
            raise HTTPException(status_code=400, detail="Mensaje vacío")
        
        # Verificar rate limit
        rate_limit_info = await check_rate_limit(
            request,
            chat_request.scope,
            limit_type="chat"
        )
        
        # Obtener token actual para incrementar contador
        token = request.cookies.get("session_token")
        current_used = 0
        
        if token:
            payload = decode_jwt_token(token)
            if payload:
                current_used = payload.get("messages_used", 0)
        
        # Incrementar rate limit y crear nuevo token
        new_token, new_used = increment_rate_limit(
            ip,
            chat_request.scope,
            current_used,
            limit_type="chat"
        )
        
        # Establecer cookie actualizada
        set_jwt_cookie(response, new_token)
        
        # Preparar headers de rate limit
        rate_limit_headers = rate_limit_info.to_headers()
        rate_limit_headers["X-Messages-Used"] = str(new_used)
        
        # Función generadora para streaming
        async def generate_stream():
            try:
                # Procesar mensaje con el agente
                full_response = ""
                async for token in process_chat_message(
                    sanitized_message,
                    chat_request.scope
                ):
                    full_response += token
                    yield await stream_token(token)
                
                # Guardar conversación en MongoDB
                await save_conversation(
                    ip,
                    chat_request.scope,
                    sanitized_message,
                    full_response
                )
                
                # Enviar señal de finalización
                yield await stream_done()
                
            except Exception as e:
                print(f"Error en streaming: {e}")
                yield await stream_error("Error procesando mensaje")
        
        # Calcular latencia
        latency = time.time() - start_time
        
        # Log request (asíncrono, no bloquea)
        # Nota: classification se obtiene del agente, por ahora usamos "unknown"
        await log_request(
            request_id=request_id,
            ip_hash=ip_hash,
            scope=chat_request.scope,
            status="success",
            latency=latency,
            classification="unknown"  # Se puede mejorar obteniendo del agente
        )
        
        # Retornar streaming response con headers
        return StreamingResponse(
            generate_stream(),
            media_type="application/x-ndjson",
            headers=rate_limit_headers
        )
        
    except HTTPException as e:
        latency = time.time() - start_time
        await log_request(
            request_id=request_id,
            ip_hash=ip_hash,
            scope=chat_request.scope,
            status=f"error_{e.status_code}",
            latency=latency
        )
        raise e
    except Exception as e:
        latency = time.time() - start_time
        await log_request(
            request_id=request_id,
            ip_hash=ip_hash,
            scope=chat_request.scope,
            status="error_500",
            latency=latency
        )
        raise HTTPException(status_code=500, detail="Error interno del servidor")


async def save_conversation(
    ip: str,
    scope: str,
    user_message: str,
    assistant_message: str
):
    """Guardar conversación en MongoDB."""
    collection = get_conversations_collection()
    date = get_utc_date()
    
    # Buscar conversación existente
    existing = await collection.find_one({
        "ip": ip,
        "scope": scope,
        "date": date,
        "deleted": False
    })
    
    # Crear mensajes
    user_msg = Message(
        role="user",
        content=user_message,
        timestamp=datetime.utcnow()
    )
    
    assistant_msg = Message(
        role="assistant",
        content=assistant_message,
        timestamp=datetime.utcnow()
    )
    
    if existing:
        # Actualizar conversación existente
        await collection.update_one(
            {"_id": existing["_id"]},
            {
                "$push": {
                    "messages": {
                        "$each": [
                            user_msg.model_dump(mode="json"),
                            assistant_msg.model_dump(mode="json")
                        ]
                    }
                },
                "$inc": {"messages_used": 1}
            }
        )
    else:
        # Crear nueva conversación
        await collection.insert_one({
            "ip": ip,
            "scope": scope,
            "date": date,
            "messages": [
                user_msg.model_dump(mode="json"),
                assistant_msg.model_dump(mode="json")
            ],
            "messages_used": 1,
            "deleted": False
        })
