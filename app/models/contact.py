from pydantic import BaseModel, EmailStr, Field


class EmailRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    country: str = Field(..., min_length=1, max_length=100)
    subject: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=500)


class ContactLeadDocument(BaseModel):
    name: str
    email: str
    country: str
    subject: str
    message: str
    ip: str
    timestamp: str
