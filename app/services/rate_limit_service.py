from app.config import settings
from app.db.collections import contact_leads_col
from app.models.rate_limit import RateLimitErrorResponse
from app.services.conversation_service import get_messages_used
from app.utils.datetime_utils import get_reset_at


async def check_chat_rate_limit(ip: str, scope: str, date: str) -> tuple[bool, int]:
    used = await get_messages_used(ip, scope, date)
    allowed = used < settings.CHAT_DAILY_LIMIT
    return allowed, used


async def check_email_rate_limit(ip: str, date: str) -> tuple[bool, int]:
    col = contact_leads_col()
    count = await col.count_documents({
        "ip": ip,
        "timestamp": {"$regex": f"^{date}"},
    })
    allowed = count < settings.EMAIL_DAILY_LIMIT
    return allowed, count


def build_rate_limit_response(limit: int, used: int) -> RateLimitErrorResponse:
    return RateLimitErrorResponse(
        limit=limit,
        used=used,
        reset_at=get_reset_at(),
    )
