from pydantic import BaseModel


class PromptDocument(BaseModel):
    key: str
    content: str
