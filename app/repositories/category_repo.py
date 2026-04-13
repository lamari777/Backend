import asyncpg
from typing import Optional
from app.schemas.category_schema import CategoryCreate, CategoryUpdate, CategoryOut

async def get_categories_by_business(conn: asyncpg.Connection, id_business: int) -> list[dict]:
    rows = await conn.fetch(
        "SELECT id_category, name, description_category, id_parent_category, id_business FROM Category WHERE id_business = $1", 
        id_business
    )
    return [dict(row) for row in rows]

async def get_category_by_id(conn: asyncpg.Connection, id_category: int, id_business: int) -> Optional[dict]:
    row = await conn.fetchrow(
        "SELECT id_category, name, description_category, id_parent_category, id_business FROM Category WHERE id_category = $1 AND id_business = $2",
        id_category, id_business
    )
    return dict(row) if row else None

async def create_category(conn: asyncpg.Connection, category: CategoryCreate, id_business: int) -> dict:
    row = await conn.fetchrow(
        "INSERT INTO Category (name, description_category, id_parent_category, id_business) VALUES ($1, $2, $3, $4) RETURNING id_category, name, description_category, id_parent_category, id_business",
        category.name, category.description_category, category.id_parent_category, id_business
    )
    return dict(row)

async def update_category(conn: asyncpg.Connection, id_category: int, category: CategoryUpdate, id_business: int) -> Optional[dict]:
    row = await conn.fetchrow(
        """
        UPDATE Category 
        SET 
            name = COALESCE($1, name),
            description_category = COALESCE($2, description_category),
            id_parent_category = COALESCE($3, id_parent_category)
        WHERE id_category = $4 AND id_business = $5
        RETURNING id_category, name, description_category, id_parent_category, id_business
        """,
        category.name, category.description_category, category.id_parent_category, id_category, id_business
    )
    return dict(row) if row else None

async def delete_category(conn: asyncpg.Connection, id_category: int, id_business: int) -> bool:
    result = await conn.execute(
        "DELETE FROM Category WHERE id_category = $1 AND id_business = $2", 
        id_category, id_business
    )
    return result == "DELETE 1"