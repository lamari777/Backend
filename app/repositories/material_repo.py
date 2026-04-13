import asyncpg
from typing import Optional
from app.schemas.material_schema import MaterialCreate, MaterialUpdate, MaterialOut

async def get_materials_by_business(conn: asyncpg.Connection, id_business: int) -> list[dict]:
    rows= await conn.fetch(
        """
        SELECT id_material, name_material, barcode, base_price, id_category, id_business
        FROM Material
        WHERE id_business = $1
        """, id_business
    )
    return [dict(row) for row in rows]

async def get_material_by_id(conn: asyncpg.Connection, id_business: int, id_material: int) -> Optional[dict]:
    rows= await conn.fetch(
        """
        SELECT id_material, name_material, barcode, base_price, id_category, id_business
        FROM Material
        WHERE id_business = $1 AND id_material = $2
        """, id_business, id_material
    )
    return dict(rows[0]) if rows else None

async def create_material(conn: asyncpg.Connection, id_business: int, material: MaterialCreate) -> Optional[dict]:
    rows= await conn.fetch(
        """
        INSERT INTO Material (name_material, barcode, base_price, id_category, id_business)
        VALUES ($1, $2, $3, $4, $5) RETURNING *
        """, material.name_material, material.barcode, material.base_price, material.id_category, id_business
    )
    return dict(rows[0])

async def update_material(conn: asyncpg.Connection, id_business: int, id_material: int, material: MaterialUpdate) -> Optional[dict]:
    rows= await conn.fetch(
        """
        UPDATE Material SET 
            name_material = COALESCE($1, name_material), 
            barcode = COALESCE($2, barcode), 
            base_price = COALESCE($3, base_price), 
            id_category = COALESCE($4, id_category)
        WHERE id_business = $5 AND id_material = $6 RETURNING *
        """, material.name_material, material.barcode, material.base_price, material.id_category, id_business, id_material
    )
    return dict(rows[0]) if rows else None

async def delete_material(conn: asyncpg.Connection, id_business: int, id_material: int) -> Optional[dict]:
    rows= await conn.fetch(
        """
        DELETE FROM Material WHERE id_business = $1 AND id_material = $2 RETURNING *
        """, id_business, id_material
    )
    return dict(rows[0]) if rows else None