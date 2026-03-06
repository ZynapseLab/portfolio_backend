import logging

from fastapi import APIRouter, Request

from app.models.contact import EmailRequest
from app.services.email_service import send_contact_email
from app.utils.ip import get_client_ip

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/contact", status_code=202)
async def contact(body: EmailRequest, request: Request):
    ip = get_client_ip(request)
    language = request.headers.get("Accept-Language", "en")

    await send_contact_email(body.model_dump(), ip, language)

    return {"detail": "Message sent successfully."}
