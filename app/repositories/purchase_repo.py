import asyncpg
from typing import Optional
from app.schemas.purchase_schema import PurchaseCreate, PurchaseUpdate, PurchaseOut

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
        INSERT INTO Purchase (id_supplier, purchase_date, id_business)
        VALUES ($1, $2, $3) RETURNING *
        """, purchase.id_supplier, purchase.purchase_date, id_business
    )
    return dict(rows[0])

async def update_purchase(conn: asyncpg.Connection, id_business: int, id_purchase: int, purchase: PurchaseUpdate) -> Optional[dict]:
    rows = await conn.fetch(
        """
        UPDATE Purchase SET 
            id_supplier = COALESCE($1, id_supplier), 
            purchase_date = COALESCE($2, purchase_date)
        WHERE id_business = $3 AND id_purchase = $4 RETURNING *
        """, purchase.id_supplier, purchase.purchase_date, id_business, id_purchase
    )
    return dict(rows[0])

async def delete_purchase(conn: asyncpg.Connection, id_business: int, id_purchase: int) -> Optional[dict]:
    rows = await conn.fetch(
        """
        DELETE FROM Purchase WHERE id_business = $1 AND id_purchase = $2 RETURNING *
        """, id_business, id_purchase
    )
    return dict(rows[0])