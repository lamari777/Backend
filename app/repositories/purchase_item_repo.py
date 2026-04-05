import asyncpg
from typing import Optional
from app.schemas.purchase_item_schema import PurchaseItemCreate, PurchaseItemOut

async def get_purchase_items_by_purchase(conn: asyncpg.Connection, id_purchase: int) -> list[dict]:
    rows = await conn.fetch(
        """
        SELECT * FROM PurchaseItem WHERE id_purchase = $1
        """, id_purchase
    )
    return [dict(row) for row in rows]

async def get_purchase_item_by_id(conn: asyncpg.Connection, id_purchase: int, id_purchase_item: int) -> Optional[dict]:
    rows = await conn.fetch(
        """
        SELECT * FROM PurchaseItem WHERE id_purchase = $1 AND id_purchase_item = $2
        """, id_purchase, id_purchase_item
    )
    return dict(rows[0]) if rows else None

async def create_purchase_item(conn: asyncpg.Connection, id_purchase: int, purchase_item: PurchaseItemCreate) -> Optional[dict]:
    rows = await conn.fetch(
        """
        INSERT INTO PurchaseItem (id_purchase, id_material, quantity_purchased, unit_price_purchased)
        VALUES ($1, $2, $3, $4) RETURNING *
        """, id_purchase, purchase_item.id_material, purchase_item.quantity_purchased, purchase_item.unit_price_purchased
    )
    return dict(rows[0])

async def delete_purchase_item(conn: asyncpg.Connection, id_purchase: int, id_purchase_item: int) -> Optional[dict]:
    rows = await conn.fetch(
        """
        DELETE FROM PurchaseItem WHERE id_purchase = $1 AND id_purchase_item = $2 RETURNING *
        """, id_purchase, id_purchase_item
    )
    return dict(rows[0])