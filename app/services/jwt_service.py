from datetime import timedelta

import jwt
from starlette.requests import Request
from starlette.responses import Response

from app.config import settings
from app.models.jwt_payload import JWTPayload
from app.utils.datetime_utils import utc_now


def create_token(payload: JWTPayload) -> str:
    now = utc_now()
    tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    data = payload.model_dump()
    data["exp"] = tomorrow
    return jwt.encode(data, settings.JWT_SECRET, algorithm="HS256")


def decode_token(token: str) -> JWTPayload | None:
    try:
        data = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        return JWTPayload(**data)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def set_jwt_cookie(response: Response, payload: JWTPayload) -> None:
    token = create_token(payload)
    response.set_cookie(
        key="session",
        value=token,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/",
    )


def get_jwt_from_request(request: Request) -> JWTPayload | None:
    token = request.cookies.get("session")
    if not token:
        return None
    return decode_token(token)
