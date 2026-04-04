from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class MaterialBase(BaseModel):
    name_material: str
    barcode: Optional[str] = None
    base_price: float
    id_category: Optional[int] = None

class MaterialCreate(MaterialBase):
    pass

class MaterialUpdate(MaterialBase):
    name_material: Optional[str] = None
    barcode: Optional[str] = None
    base_price: Optional[float] = None
    id_category: Optional[int] = None

class MaterialOut(MaterialBase):
    id_material: int
    id_business: int

    class Config:
        from_attributes = True
