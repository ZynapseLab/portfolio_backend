"""Modelos para chat."""
from pydantic import BaseModel, Field
from typing import Literal


class ChatRequest(BaseModel):
    """Request para endpoint /chat."""
    message: str = Field(..., min_length=1, max_length=2000)
    scope: Literal["global", "jonathan", "pablo"] = Field(..., description="Scope de la conversación")


class RateLimitError(BaseModel):
    """Error de rate limit."""
    type: Literal["rate_limit"] = "rate_limit"
    limit: int
    used: int
    reset_at: str  # ISO8601
