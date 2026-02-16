"""Modelos para contacto."""
from pydantic import BaseModel, EmailStr, Field


class ContactRequest(BaseModel):
    """Request para tool de contacto."""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    country: str = Field(..., min_length=1, max_length=100)
    subject: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=500)
