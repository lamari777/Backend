from pydantic import BaseModel
from typing import Optional

class SaleItemCreate(BaseModel):
    """Datos que el cliente envía en el body. id_sale viene del path de la URL."""
    id_material: int
    quantity_sold: int

class SaleItemOut(BaseModel):
    """Datos que devuelve la API, incluyendo los IDs generados por la BD."""
    id_sale_item: int
    id_sale: int
    id_material: int
    quantity_sold: int

    class Config:
        from_attributes = True