import asyncpg
from typing import Optional
from app.schemas.supplier_schema import SupplierCreate, SupplierUpdate, SupplierOut

async def get_suppliers_by_business(conn: asyncpg.Connection, id_business: int) -> list[dict]:
    rows = await conn.fetch(
        """
        SELECT *
        FROM Supplier 
        WHERE id_business = $1
        """, id_business
    )
    return [dict(row) for row in rows]


async def get_supplier_by_id(conn: asyncpg.Connection, id_business: int, id_supplier:int) -> Optional[dict]:
    rows = await conn.fetch(
        """
        SELECT *
        FROM Supplier
        WHERE id_business = $1 AND id_supplier = $2
        """, id_business, id_supplier
    )
    return dict(rows[0]) if rows else None

async def create_supplier(conn: asyncpg.Connection, id_business: int, supplier: SupplierCreate) -> Optional[dict]:
    rows = await conn.fetch(
        """
        INSERT INTO Supplier (name, supplier_phone_number, description, email, id_business)
        VALUES ($1, $2, $3, $4, $5) RETURNING *
        """, supplier.name, supplier.supplier_phone_number, supplier.description, supplier.email, id_business
    )
    return dict(rows[0])

async def update_supplier(conn: asyncpg.Connection, id_business: int, id_supplier: int, supplier: SupplierUpdate) -> Optional[dict]:
    rows = await conn.fetch(
        """
        UPDATE Supplier SET 
            name = COALESCE($1, name), 
            supplier_phone_number = COALESCE($2, supplier_phone_number), 
            description = COALESCE($3, description), 
            email = COALESCE($4, email)
        WHERE id_business = $5 AND id_supplier = $6 
        RETURNING *
        """, supplier.name, supplier.supplier_phone_number, supplier.description, supplier.email, id_business, id_supplier
    )
    return dict(rows[0]) if rows else None

async def delete_supplier(conn: asyncpg.Connection, id_business: int, id_supplier: int) -> Optional[dict]:
    rows = await conn.fetch(
        """
        DELETE FROM Supplier WHERE id_business = $1 AND id_supplier = $2 RETURNING *
        """, id_business, id_supplier
    )
    return dict(rows[0]) if rows else None