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
    material_exists = await conn.fetchval(
        "SELECT 1 FROM Material WHERE id_material = $1 AND id_business = $2",
        product.id_material, id_business
    )
    if not material_exists:
        return None

    rows = await conn.fetch(
        """
        INSERT INTO Product (id_material, expiration_date, quantity, entry_date, id_supplier, id_purchase_item)
        VALUES ($1, $2, $3, $4, $5, $6) RETURNING *
        """, 
        product.id_material, 
        product.expiration_date, 
        product.quantity, 
        product.entry_date,
        product.id_supplier,
        product.id_purchase_item
    )
    result = dict(rows[0])
    result["id_business"] = id_business
    return result

async def update_product(conn: asyncpg.Connection, id_business: int, batch_number: int, product: ProductUpdate) -> Optional[dict]:
    rows = await conn.fetch(
        """
        UPDATE Product p SET 
            expiration_date = COALESCE($1, p.expiration_date), 
            quantity = COALESCE($2, p.quantity), 
            entry_date = COALESCE($3, p.entry_date),
            id_supplier = COALESCE($4, p.id_supplier),
            id_purchase_item = COALESCE($5, p.id_purchase_item)
        FROM Material m
        WHERE p.id_material = m.id_material 
          AND m.id_business = $6 
          AND p.batch_number = $7 
        RETURNING p.*, m.id_business
        """, 
        product.expiration_date, 
        product.quantity, 
        product.entry_date, 
        product.id_supplier,
        product.id_purchase_item,
        id_business, 
        batch_number
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