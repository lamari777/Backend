import asyncpg
from typing import Optional
from app.schemas.business_schema import BusinessCreate, BusinessUpdate
from app.core.security import hash_password

async def get_all_businesses(conn: asyncpg.Connection) -> list[dict]:
    rows = await conn.fetch("SELECT id_business, name_business, email_business, business_phone_number FROM Business")
    return [dict(row) for row in rows]

async def get_business_by_id(conn: asyncpg.Connection, id_business: int) -> Optional[dict]:
    row = await conn.fetchrow(
        "SELECT id_business, name_business, email_business, business_phone_number FROM Business WHERE id_business = $1", 
        id_business
    )
    return dict(row) if row else None

async def create_business(conn: asyncpg.Connection, business: BusinessCreate) -> dict:
    hashed_password = hash_password(business.password_business)
    row = await conn.fetchrow(
        """
        INSERT INTO Business (name_business, email_business, password_business, business_phone_number)
        VALUES ($1, $2, $3, $4)
        RETURNING id_business, name_business, email_business, business_phone_number
        """,
        business.name_business,
        business.email_business,
        hashed_password,
        business.business_phone_number
    )
    return dict(row)

async def update_business(conn: asyncpg.Connection, id_business: int, business: BusinessUpdate) -> Optional[dict]:
    fields = business.model_dump(exclude_none=True)
    if not fields:
        return await get_business_by_id(conn, id_business)
    
    if "password_business" in fields:
        fields["password_business"] = hash_password(fields["password_business"])
        
    set_clause = ", ".join(f"{key} = ${i+2}" for i, key in enumerate(fields.keys()))
    values = list(fields.values())

    query = f"""
        UPDATE Business
        SET {set_clause}
        WHERE id_business = $1
        RETURNING id_business, name_business, email_business, business_phone_number
    """
    row = await conn.fetchrow(query, id_business, *values)
    return dict(row) if row else None

async def delete_business(conn: asyncpg.Connection, id_business: int) -> bool:
    result = await conn.execute("DELETE FROM Business WHERE id_business = $1", id_business)
    return result == "DELETE 1"
