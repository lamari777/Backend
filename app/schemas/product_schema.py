from pydantic import BaseModel
from typing import Optional
from datetime import date

class ProductBase(BaseModel):
    id_material: int
    expiration_date: Optional[date] = None
    quantity: Optional[int] = 0
    entry_date: Optional[date] = None
    id_supplier: Optional[int] = None
    id_purchase_item: Optional[int] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    expiration_date: Optional[date] = None
    entry_date: Optional[date] = None
    quantity: Optional[int] = None
    id_supplier: Optional[int] = None
    id_purchase_item: Optional[int] = None

class ProductOut(ProductBase):
    batch_number: int
    id_business: int

    class Config:
        from_attributes = True