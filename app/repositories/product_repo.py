import asyncpg
from typing import Optional
from app.schemas.product_schema import ProductCreate, ProductUpdate, ProductOut

async def get_products_by_business(conn: asyncpg.Connection, id_business: int) -> list[dict]:
    rows = await conn.fetch(
        """
        SELECT p.*, m.id_business 
        FROM Product p
        JOIN Material m ON p.id_material = m.id_material
        WHERE m.id_business = $1
        """, id_business
    )
    return [dict(row) for row in rows]

async def get_product_by_id(conn: asyncpg.Connection, id_business: int, batch_number: int) -> Optional[dict]:
    rows = await conn.fetch(
        """
        SELECT p.*, m.id_business
        FROM Product p
        JOIN Material m ON p.id_material = m.id_material
        WHERE m.id_business = $1 AND p.batch_number = $2
        """, id_business, batch_number
    )
    return dict(rows[0]) if rows else None

async def create_product(conn: asyncpg.Connection, id_business: int, product: ProductCreate) -> Optional[dict]:
    # Verificar primero que el material pertenece al negocio
    material_exists = await conn.fetchval(
        "SELECT 1 FROM Material WHERE id_material = $1 AND id_business = $2",
        product.id_material, id_business
    )
    if not material_exists:
        return None

    rows = await conn.fetch(
        """
        INSERT INTO Product (id_material, expiration_date, quantity, entry_date)
        VALUES ($1, $2, $3, $4) RETURNING *, $5 as id_business
        """, product.id_material, product.expiration_date, product.quantity, product.entry_date, id_business
    )
    return dict(rows[0])

async def update_product(conn: asyncpg.Connection, id_business: int, batch_number: int, product: ProductUpdate) -> Optional[dict]:
    rows = await conn.fetch(
        """
        UPDATE Product p SET 
            id_material = COALESCE($1, p.id_material), 
            expiration_date = COALESCE($2, p.expiration_date), 
            quantity = COALESCE($3, p.quantity), 
            entry_date = COALESCE($4, p.entry_date)
        FROM Material m
        WHERE p.id_material = m.id_material 
          AND m.id_business = $5 
          AND p.batch_number = $6 
        RETURNING p.*, m.id_business
        """, product.id_material, product.expiration_date, product.quantity, product.entry_date, id_business, batch_number
    )
    return dict(rows[0]) if rows else None

async def delete_product(conn: asyncpg.Connection, id_business: int, batch_number: int) -> Optional[dict]:
    rows = await conn.fetch(
        """
        DELETE FROM Product 
        USING Material 
        WHERE Product.id_material = Material.id_material 
          AND Material.id_business = $1 
          AND Product.batch_number = $2 
        RETURNING Product.*, Material.id_business
        """, id_business, batch_number
    )
    return dict(rows[0]) if rows else None