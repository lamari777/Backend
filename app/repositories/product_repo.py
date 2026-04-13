import asyncpg
from typing import Optional
from app.schemas.product_schema import ProductCreate, ProductUpdate, ProductOut

async def get_products_by_business(conn: asyncpg.Connection, id_business: int) -> list[dict]:
    rows = await conn.fetch(
        """
        SELECT * FROM Product WHERE id_business = $1
        """, id_business
    )
    return [dict(row) for row in rows]

async def get_product_by_id(conn: asyncpg.Connection, id_business: int, id_product: int) -> Optional[dict]:
    rows = await conn.fetch(
        """
        SELECT * FROM Product WHERE id_business = $1 AND id_product = $2
        """, id_business, id_product
    )
    return dict(rows[0]) if rows else None

async def create_product(conn: asyncpg.Connection, id_business: int, product: ProductCreate) -> Optional[dict]:
    rows = await conn.fetch(
        """
        INSERT INTO Product (id_material, expiration_date, quantity, entry_date, id_business)
        VALUES ($1, $2, $3, $4, $5) RETURNING *
        """, product.id_material, product.expiration_date, product.quantity, product.entry_date, id_business
    )
    return dict(rows[0])

async def update_product(conn: asyncpg.Connection, id_business: int, id_product: int, product: ProductUpdate) -> Optional[dict]:
    rows = await conn.fetch(
        """
        UPDATE Product SET 
            id_material = COALESCE($1, id_material), 
            expiration_date = COALESCE($2, expiration_date), 
            quantity = COALESCE($3, quantity), 
            entry_date = COALESCE($4, entry_date)
        WHERE id_business = $5 AND id_product = $6 RETURNING *
        """, product.id_material, product.expiration_date, product.quantity, product.entry_date, id_business, id_product
    )
    return dict(rows[0]) if rows else None

async def delete_product(conn: asyncpg.Connection, id_business: int, id_product: int) -> Optional[dict]:
    rows = await conn.fetch(
        """
        DELETE FROM Product WHERE id_business = $1 AND id_product = $2 RETURNING *
        """, id_business, id_product
    )
    return dict(rows[0]) if rows else None