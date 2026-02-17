from pydantic import BaseModel, Field


class KnowledgeDocument(BaseModel):
    source_id: str
    scope: str
    sections: list[str] = Field(default_factory=list)
    embedding: list[float] = Field(default_factory=list)
