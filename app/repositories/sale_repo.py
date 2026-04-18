import asyncpg
from typing import Optional
from app.schemas.sale_schema import SaleCreate, SaleOut, SaleWithItemsCreate

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

from app.repositories.sale_item_repo import create_sale_item

async def create_sale_with_items(conn: asyncpg.Connection, id_business: int, sale_data: SaleWithItemsCreate) -> dict:
    async with conn.transaction():
        sale_row = await conn.fetchrow(
            """
            INSERT INTO Sale (sale_date, id_business)
            VALUES ($1, $2) RETURNING *
            """, sale_data.sale_date, id_business
        )
        id_sale = sale_row['id_sale']

        for item in sale_data.items:
            await create_sale_item(conn, id_sale, id_business, item)

        return dict(sale_row)