import asyncpg
from typing import Optional
from app.schemas.material_schema import MaterialCreate, MaterialUpdate, MaterialOut

async def get_materials_by_business(conn: asyncpg.Connection, id_business: int) -> list[dict]:
    rows= await conn.fetch(
        """
        SELECT id_material, material_name, bar_code, base_price,min_stock, id_category, id_business
        FROM Material
        WHERE id_business = $1
        """, id_business
    )
    return [dict(row) for row in rows]

async def get_material_by_id(conn: asyncpg.Connection, id_business: int, id_material: int) -> Optional[dict]:
    rows= await conn.fetch(
        """
        SELECT id_material, material_name, bar_code, base_price, min_stock, id_category, id_business
        FROM Material
        WHERE id_business = $1 AND id_material = $2
        """, id_business, id_material
    )
    return dict(rows[0]) if rows else None

async def create_material(conn: asyncpg.Connection, id_business: int, material: MaterialCreate) -> Optional[dict]:
    rows= await conn.fetch(
        """
        INSERT INTO Material (material_name, bar_code, base_price, min_stock, id_category, id_business)
        VALUES ($1, $2, $3, $4, $5, $6) RETURNING *
        """, material.material_name, material.bar_code, material.base_price, material.min_stock, material.id_category, id_business
    )
    return dict(rows[0])

async def update_material(conn: asyncpg.Connection, id_business: int, id_material: int, material: MaterialUpdate) -> Optional[dict]:
    current_cat = await conn.fetchval("SELECT id_category FROM Material WHERE id_material = $1", id_material)
    update_data = material.model_dump(exclude_unset=True)
    category_to_save = update_data.get("id_category", current_cat)

    rows = await conn.fetch(
        """
        UPDATE Material SET 
            material_name = COALESCE($1, material_name), 
            bar_code = COALESCE($2, bar_code), 
            base_price = COALESCE($3, base_price), 
            min_stock = COALESCE($4, min_stock), 
            id_category = $5
        WHERE id_business = $6 AND id_material = $7 
        RETURNING *
        """, 
        material.material_name, material.bar_code, material.base_price, material.min_stock, 
        category_to_save, id_business, id_material
    )
    return dict(rows[0]) if rows else None

async def delete_material(conn: asyncpg.Connection, id_business: int, id_material: int) -> Optional[dict]:
    rows= await conn.fetch(
        """
        DELETE FROM Material WHERE id_business = $1 AND id_material = $2 RETURNING *
        """, id_business, id_material
    )
    return dict(rows[0]) if rows else None