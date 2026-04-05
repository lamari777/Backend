from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PurchaseBase(BaseModel):
    id_supplier: Optional[int] = None
    purchase_date: Optional[datetime] = None

class PurchaseCreate(PurchaseBase):
    pass

class PurchaseUpdate(BaseModel):
    id_supplier: Optional[int] = None
    purchase_date: Optional[datetime] = None

class PurchaseOut(PurchaseBase):
    id_purchase: int
    id_business: int 
    class Config:
        from_attributes = True