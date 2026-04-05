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