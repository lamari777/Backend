from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PurchaseBase(BaseModel):
    purchase_date: Optional[datetime] = None

class PurchaseCreate(PurchaseBase):
    pass

class PurchaseOut(PurchaseBase):
    id_purchase: int
    id_business: int 
    class Config:
        from_attributes = True

class PurchaseItemWithProductCreate(BaseModel):
    id_material: int
    quantity: int
    id_supplier: Optional[int] = None
    unit_price: float
    expiration_date: Optional[datetime] = None
    entry_date: Optional[datetime] = None

class PurchaseWithItemsCreate(PurchaseBase):
    items: list[PurchaseItemWithProductCreate]