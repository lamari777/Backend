import asyncpg
from typing import Optional
from app.schemas.purchase_schema import PurchaseCreate, PurchaseOut

async def get_purchases_by_business(conn: asyncpg.Connection, id_business: int) -> list[dict]:
    rows = await conn.fetch(
        """
        SELECT * FROM Purchase WHERE id_business = $1
        """, id_business
    )
    return [dict(row) for row in rows]

async def get_purchase_by_id(conn: asyncpg.Connection, id_business: int, id_purchase: int) -> Optional[dict]:
    rows = await conn.fetch(
        """
        SELECT * FROM Purchase WHERE id_business = $1 AND id_purchase = $2
        """, id_business, id_purchase
    )
    return dict(rows[0]) if rows else None

async def create_purchase(conn: asyncpg.Connection, id_business: int, purchase: PurchaseCreate) -> Optional[dict]:
    rows = await conn.fetch(
        """
        INSERT INTO Purchase (purchase_date, id_business)
        VALUES ($1, $2) RETURNING *
        """, purchase.purchase_date, id_business
    )
    return dict(rows[0])

async def delete_purchase(conn: asyncpg.Connection, id_business: int, id_purchase: int) -> Optional[dict]:
    rows = await conn.fetch(
        """
        DELETE FROM Purchase WHERE id_business = $1 AND id_purchase = $2 RETURNING *
        """, id_business, id_purchase
    )
    return dict(rows[0])