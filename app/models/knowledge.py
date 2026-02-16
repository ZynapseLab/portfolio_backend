"""Modelos para knowledge base."""
from pydantic import BaseModel
from typing import Dict, List


class KnowledgeDocument(BaseModel):
    """Documento en knowledge_base."""
    scope: str  # "global", "jonathan", "pablo"
    sections: Dict[str, str]  # experience, skills, projects, services
    embedding: List[float]
