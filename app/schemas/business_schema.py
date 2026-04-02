from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class BusinessBase(BaseModel):
    name_business: str
    email_business: EmailStr
    business_phone_number: Optional[str] = None

class BusinessCreate(BusinessBase):
    password_business: str = Field(..., max_length=72)

class BusinessUpdate(BaseModel):
    name_business: Optional[str] = None
    email_business: Optional[EmailStr] = None
    password_business: Optional[str] = None
    business_phone_number: Optional[str] = None

class BusinessOut(BusinessBase):
    id_business: int

    class Config:
        from_attributes = True
