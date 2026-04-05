from pydantic import BaseModel
from typing import Optional

class SaleItemBase(BaseModel):
    id_sale: int
    id_material: int
    quantity_sold: int

class SaleItemCreate(SaleItemBase):
    pass

class SaleItemOut(SaleItemBase):
    id_sale_item: int

    class Config:
        from_attributes = True  