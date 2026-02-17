from typing import Literal

from pydantic import BaseModel, Field


class MessageEntry(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ConversationDocument(BaseModel):
    ip: str
    scope: str
    date: str
    messages: list[MessageEntry] = Field(default_factory=list)
    messages_used: int = 0
    deleted: bool = False
