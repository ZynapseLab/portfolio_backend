"""Modelos para conversaciones."""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class Message(BaseModel):
    """Mensaje individual en conversación."""
    role: str  # "user" o "assistant"
    content: str
    timestamp: datetime


class Conversation(BaseModel):
    """Modelo de conversación en MongoDB."""
    ip: str
    scope: str
    date: str  # YYYY-MM-DD
    messages: List[Message] = []
    messages_used: int = 0
    deleted: bool = False
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
