from pydantic import BaseModel


class JWTPayload(BaseModel):
    ip: str
    scope: str
    messages_used: int
    date: str
