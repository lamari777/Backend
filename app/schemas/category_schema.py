from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class CategoryBase(BaseModel):
    name_category: str
    description_category: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    name_category: Optional[str] = None
    pass

class CategoryOut(CategoryBase):
    id_category: int
    id_business: int

    class Config:
        from_attributes = True
