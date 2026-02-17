from typing import Literal

from pydantic import BaseModel


class RateLimitErrorResponse(BaseModel):
    type: Literal["rate_limit"] = "rate_limit"
    limit: int
    used: int
    reset_at: str
