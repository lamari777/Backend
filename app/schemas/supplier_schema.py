from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class SupplierBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    supplier_phone_number: str
    description: Optional[str] = None

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(SupplierBase):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    supplier_phone_number: Optional[str] = None
    description: Optional[str] = None

class SupplierOut(SupplierBase):
    id_supplier: int
    id_business: int

    class Config:
        from_attributes = True