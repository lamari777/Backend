import asyncpg
from typing import Optional
from app.schemas.sale_item_schema import SaleItemCreate, SaleItemOut

async def get_sale_items_by_sale(conn: asyncpg.Connection, id_sale: int) -> list[dict]:
    rows = await conn.fetch(
        """
        SELECT sale_item.*, material.base_price FROM sale_item JOIN material ON sale_item.id_material = material.id_material WHERE id_sale = $1
        """, id_sale
    )
    return [dict(row) for row in rows]

async def get_sale_item_by_id(conn: asyncpg.Connection, id_sale: int, id_sale_item: int) -> Optional[dict]:
    rows = await conn.fetch(
        """
        SELECT sale_item.*, material.base_price FROM sale_item JOIN material ON sale_item.id_material = material.id_material WHERE id_sale = $1 AND id_sale_item = $2
        """, id_sale, id_sale_item
    )
    return dict(rows[0]) if rows else None

async def create_sale_item(conn: asyncpg.Connection, id_sale: int, id_business: int, sale_item: SaleItemCreate) -> Optional[dict]:
    """
    Crea un item de venta y descuenta automáticamente el stock de los lotes (Product)
    siguiendo la lógica FEFO (First Expired, First Out) y FIFO como fallback.
    Todo se realiza dentro de una transacción implícita si se llama con una conexión 
    que ya tiene una transacción abierta, o podemos manejarla aquí.
    """
    async with conn.transaction():
        # Ordenamos por fecha de caducidad (FEFO) y luego por fecha de entrada (FIFO).
        batches = await conn.fetch(
            """
            SELECT p.batch_number, p.quantity 
            FROM Product p
            JOIN Material m ON p.id_material = m.id_material
            WHERE p.id_material = $1 AND m.id_business = $2 AND p.quantity > 0
            ORDER BY p.expiration_date ASC NULLS LAST, p.entry_date ASC
            FOR UPDATE
            """,
            sale_item.id_material, id_business
        )

        total_available = sum(b['quantity'] for b in batches)
        if total_available < sale_item.quantity_sold:
            raise ValueError(f"Stock insuficiente. Disponible: {total_available}, Solicitado: {sale_item.quantity_sold}")

        remaining_to_deduct = sale_item.quantity_sold
        for batch in batches:
            if remaining_to_deduct <= 0:
                break
            
            batch_id = batch['batch_number']
            batch_qty = batch['quantity']

            if batch_qty > remaining_to_deduct:
                await conn.execute(
                    "UPDATE Product SET quantity = quantity - $1 WHERE batch_number = $2",
                    remaining_to_deduct, batch_id
                )
                remaining_to_deduct = 0
            else:
                await conn.execute(
                    "DELETE FROM Product WHERE batch_number = $1",
                    batch_id
                )
                remaining_to_deduct -= batch_qty

        rows = await conn.fetch(
            """
            INSERT INTO sale_item (id_sale, id_material, quantity_sold)
            VALUES ($1, $2, $3) RETURNING *
            """, id_sale, sale_item.id_material, sale_item.quantity_sold
        )
        return dict(rows[0])

async def delete_sale_item(conn: asyncpg.Connection, id_sale: int, id_sale_item: int) -> Optional[dict]:
    rows = await conn.fetch(
        """
        DELETE FROM sale_item WHERE id_sale = $1 AND id_sale_item = $2 RETURNING *
        """, id_sale, id_sale_item
    )
    return dict(rows[0]) if rows else None