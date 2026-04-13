from pydantic import BaseModel
from typing import Optional

class PurchaseItemCreate(BaseModel):
    """Datos que el cliente envía en el body. id_purchase viene del path de la URL."""
    id_supplier: Optional[int] = None
    id_material: int
    quantity_purchased: int
    unit_price_purchased: float

class PurchaseItemOut(BaseModel):
    """Datos que devuelve la API, incluyendo los IDs generados por la BD."""
    id_purchase_item: int
    id_purchase: int
    id_supplier: Optional[int] = None
    id_material: int
    quantity_purchased: int
    unit_price_purchased: float

    class Config:
        from_attributes = True