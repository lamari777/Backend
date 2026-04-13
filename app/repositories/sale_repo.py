import asyncpg
from typing import Optional
from app.schemas.sale_schema import SaleCreate, SaleOut

async def get_sales_by_business(conn: asyncpg.Connection, id_business: int) -> list[dict]:
    rows = await conn.fetch(
        """
        SELECT * FROM Sale WHERE id_business = $1
        """, id_business
    )
    return [dict(row) for row in rows]

async def get_sale_by_id(conn: asyncpg.Connection, id_business: int, id_sale: int) -> Optional[dict]:
    rows = await conn.fetch(
        """
        SELECT * FROM Sale WHERE id_business = $1 AND id_sale = $2
        """, id_business, id_sale
    )
    return dict(rows[0]) if rows else None

async def create_sale(conn: asyncpg.Connection, id_business: int, sale: SaleCreate) -> Optional[dict]:
    rows = await conn.fetch(
        """
        INSERT INTO Sale (sale_date, id_business)
        VALUES ($1, $2) RETURNING *
        """, sale.sale_date, id_business
    )
    return dict(rows[0])

async def delete_sale(conn: asyncpg.Connection, id_business: int, id_sale: int) -> Optional[dict]:
    rows = await conn.fetch(
        """
        DELETE FROM Sale WHERE id_business = $1 AND id_sale = $2 RETURNING *
        """, id_business, id_sale
    )
    return dict(rows[0]) if rows else None