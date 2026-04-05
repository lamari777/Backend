import asyncpg
from typing import Optional
from app.schemas.sale_item_schema import SaleItemCreate, SaleItemOut

async def get_sale_items_by_sale(conn: asyncpg.Connection, id_sale: int) -> list[dict]:
    rows = await conn.fetch(
        """
        SELECT SaleItem.*, Material.base_price FROM SaleItem JOIN Material ON SaleItem.id_material = Material.id_material WHERE id_sale = $1
        """, id_sale
    )
    return [dict(row) for row in rows]

async def get_sale_item_by_id(conn: asyncpg.Connection, id_sale: int, id_sale_item: int) -> Optional[dict]:
    rows = await conn.fetch(
        """
        SELECT SaleItem.*, Material.base_price FROM SaleItem JOIN Material ON SaleItem.id_material = Material.id_materialWHERE id_sale = $1 AND id_sale_item = $2
        """, id_sale, id_sale_item
    )
    return dict(rows[0]) if rows else None

async def create_sale_item(conn: asyncpg.Connection, id_sale: int, sale_item: SaleItemCreate) -> Optional[dict]:
    rows = await conn.fetch(
        """
        INSERT INTO SaleItem (id_sale, id_material, quantity_sold)
        VALUES ($1, $2, $3) RETURNING *
        """, id_sale, sale_item.id_material, sale_item.quantity_sold
    )
    return dict(rows[0])

async def delete_sale_item(conn: asyncpg.Connection, id_sale: int, id_sale_item: int) -> Optional[dict]:
    rows = await conn.fetch(
        """
        DELETE FROM SaleItem WHERE id_sale = $1 AND id_sale_item = $2 RETURNING *
        """, id_sale, id_sale_item
    )
    return dict(rows[0])