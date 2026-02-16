"""Modelos para rate limiting."""
from pydantic import BaseModel
from datetime import datetime


class RateLimitInfo(BaseModel):
    """Información de rate limit."""
    used: int
    limit: int
    reset_at: datetime  # UTC
    
    def to_headers(self) -> dict:
        """Convertir a headers HTTP."""
        return {
            "X-Messages-Used": str(self.used),
            "X-Messages-Limit": str(self.limit),
            "X-Reset-At": self.reset_at.isoformat()
        }
