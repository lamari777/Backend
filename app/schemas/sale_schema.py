from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SaleBase(BaseModel):
    sale_date: Optional[datetime] = None

class SaleCreate(SaleBase):
    pass

class SaleOut(SaleBase):
    id_sale: int
    id_business: int 
    class Config:
        from_attributes = True

from app.schemas.sale_item_schema import SaleItemCreate

class SaleWithItemsCreate(SaleBase):
    items: list[SaleItemCreate]