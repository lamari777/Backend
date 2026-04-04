from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class SupplierBase(BaseModel):
    name_supplier: str
    email_supplier: Optional[EmailStr] = None
    phone_supplier: str
    description_supplier: Optional[str] = None

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(SupplierBase):
    name_supplier: Optional[str] = None
    email_supplier: Optional[EmailStr] = None
    phone_supplier: Optional[str] = None
    description_supplier: Optional[str] = None

class SupplierOut(SupplierBase):
    id_supplier: int
    id_business: int

    class Config:
        from_attributes = True