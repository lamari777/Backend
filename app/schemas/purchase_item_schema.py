from pydantic import BaseModel
from typing import Optional

class PurchaseItemBase(BaseModel):
    id_purchase: int
    id_material: int
    quantity_purchased: int
    unit_price_purchased: float

class PurchaseItemCreate(PurchaseItemBase):
    pass

class PurchaseItemOut(PurchaseItemBase):
    id_purchase_item: int

    class Config:
        from_attributes = True