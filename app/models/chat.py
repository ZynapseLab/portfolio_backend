from typing import Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    scope: Literal["global", "jonathan", "pablo"] = "global"


class TokenChunk(BaseModel):
    type: Literal["token"] = "token"
    data: str


class DoneChunk(BaseModel):
    type: Literal["done"] = "done"
