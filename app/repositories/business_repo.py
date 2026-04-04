import asyncpg
from typing import Optional
from app.schemas.business_schema import BusinessCreate, BusinessUpdate
from app.core.security import hash_password, verify_password

async def get_all_businesses(conn: asyncpg.Connection) -> list[dict]:
    rows = await conn.fetch("SELECT id_business, name_business, email_business, business_phone_number FROM Business")
    return [dict(row) for row in rows]

async def get_business_by_id(conn: asyncpg.Connection, id_business: int) -> Optional[dict]:
    row = await conn.fetchrow(
        "SELECT id_business, name_business, email_business, business_phone_number FROM Business WHERE id_business = $1", 
        id_business
    )
    return dict(row) if row else None

async def get_business_by_email(conn: asyncpg.Connection, email: str) -> Optional[dict]:
    """Devuelve el negocio completo (incluida la contraseña hasheada) filtrando por email."""
    row = await conn.fetchrow(
        "SELECT id_business, name_business, email_business, password_business, business_phone_number "
        "FROM Business WHERE email_business = $1",
        email
    )
    return dict(row) if row else None

async def get_business_by_name(conn: asyncpg.Connection, name: str) -> Optional[dict]:
    """Devuelve el negocio completo (incluida la contraseña hasheada) filtrando por nombre."""
    row = await conn.fetchrow(
        "SELECT id_business, name_business, email_business, password_business, business_phone_number "
        "FROM Business WHERE name_business = $1",
        name
    )
    return dict(row) if row else None

async def authenticate_business(conn: asyncpg.Connection, identifier: str, password: str) -> Optional[dict]:
    """Busca un negocio por email o nombre y verifica la contraseña.
    Devuelve el negocio (sin password) si las credenciales son correctas, o None si no.
    """
    business = await get_business_by_email(conn, identifier)
    if not business:
        business = await get_business_by_name(conn, identifier)
    if not business:
        return None
    if not verify_password(password, business["password_business"]):
        return None
    business.pop("password_business", None)
    return business

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
    new_password = hash_password(business.password_business) if business.password_business else None

    row = await conn.fetchrow(
        """
        UPDATE Business
        SET 
            name_business = COALESCE($1, name_business),
            email_business = COALESCE($2, email_business),
            password_business = COALESCE($3, password_business),
            business_phone_number = COALESCE($4, business_phone_number)
        WHERE id_business = $5
        RETURNING id_business, name_business, email_business, business_phone_number
        """,
        business.name_business,
        business.email_business,
        new_password,
        business.business_phone_number,
        id_business
    )
    return dict(row) if row else None

async def delete_business(conn: asyncpg.Connection, id_business: int) -> bool:
    result = await conn.execute("DELETE FROM Business WHERE id_business = $1", id_business)
    return result == "DELETE 1"
