import asyncpg
from typing import Optional
from app.schemas.supplier_schema import SupplierCreate, SupplierUpdate, SupplierOut

async def get_suppliers_by_business(conn: asyncpg.Connection, id_business: int) -> list[dict]:
    rows = await conn.fetch(
        """
        SELECT id_supplier, name_supplier, phone_supplier, description_supplier, email_supplier 
        FROM Supplier 
        WHERE id_business = $1
        """, id_business
    )
    return [dict(row) for row in rows]


async def get_supplier_by_id(conn: asyncpg.Connection, id_business: int, id_supplier:int) -> Optional[dict]:
    rows = await conn.fetch(
        """
        SELECT name_supplier, phone_supplier, description_supplier, email_supplier 
        FROM Supplier
        WHERE id_business = $1 AND id_supplier = $2
        """, id_business, id_supplier
    )
    return dict(rows[0])

async def create_supplier(conn: asyncpg.Connection, id_business: int, supplier: SupplierCreate) -> Optional[dict]:
    rows = await conn.fetch(
        """
        INSERT INTO Supplier (name_supplier, phone_supplier, description_supplier, email_supplier, id_business)
        VALUES ($1, $2, $3, $4, $5) RETURNING id_supplier
        """, supplier.name_supplier, supplier.phone_supplier, supplier.description_supplier, supplier.email_supplier, id_business
    )
    return dict(rows[0])

async def update_supplier(conn: asyncpg.Connection, id_business: int, id_supplier: int, supplier: SupplierUpdate) -> Optional[dict]:
    rows = await conn.fetch(
        """
        UPDATE Supplier SET name_supplier = $1, phone_supplier = $2, description_supplier = $3, email_supplier = $4
        WHERE id_business = $5 AND id_supplier = $6 RETURNING id_supplier
        """, supplier.name_supplier, supplier.phone_supplier, supplier.description_supplier, supplier.email_supplier, id_business, id_supplier
    )
    return dict(rows[0])

async def delete_supplier(conn: asyncpg.Connection, id_business: int, id_supplier: int) -> Optional[dict]:
    rows = await conn.fetch(
        """
        DELETE FROM Supplier WHERE id_business = $1 AND id_supplier = $2 RETURNING id_supplier
        """, id_business, id_supplier
    )
    return dict(rows[0])