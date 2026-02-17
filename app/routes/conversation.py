from fastapi import APIRouter, Request, Response

from app.models.jwt_payload import JWTPayload
from app.services.conversation_service import soft_delete_conversation
from app.services.jwt_service import get_jwt_from_request, set_jwt_cookie
from app.utils.datetime_utils import utc_today
from app.utils.ip import get_client_ip

router = APIRouter()


@router.delete("/conversation")
async def delete_conversation(request: Request):
    ip = get_client_ip(request)
    payload = get_jwt_from_request(request)
    date = utc_today()

    scope = payload.scope if payload else "global"
    deleted = await soft_delete_conversation(ip, scope, date)

    response = Response(status_code=200)
    new_payload = JWTPayload(
        ip=ip,
        scope=scope,
        messages_used=payload.messages_used if payload else 0,
        date=date,
    )
    set_jwt_cookie(response, new_payload)

    if deleted:
        return response
    response.status_code = 404
    return response
