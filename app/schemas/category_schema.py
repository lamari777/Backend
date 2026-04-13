from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class CategoryBase(BaseModel):
    name: str
    description_category: Optional[str] = None
    id_parent_category: Optional[int] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description_category: Optional[str] = None
    id_parent_category: Optional[int] = None

class CategoryOut(CategoryBase):
    id_category: int
    id_business: int

    class Config:
        from_attributes = True
