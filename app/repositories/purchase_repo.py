import asyncpg
from typing import Optional
from app.schemas.purchase_schema import PurchaseCreate, PurchaseOut, PurchaseWithItemsCreate

async def get_purchases_by_business(conn: asyncpg.Connection, id_business: int) -> list[dict]:
    rows = await conn.fetch(
        """
        SELECT * FROM Purchase WHERE id_business = $1
        """, id_business
    )
    return [dict(row) for row in rows]

async def get_purchase_by_id(conn: asyncpg.Connection, id_business: int, id_purchase: int) -> Optional[dict]:
    rows = await conn.fetch(
        """
        SELECT * FROM Purchase WHERE id_business = $1 AND id_purchase = $2
        """, id_business, id_purchase
    )
    return dict(rows[0]) if rows else None

async def create_purchase(conn: asyncpg.Connection, id_business: int, purchase: PurchaseCreate) -> Optional[dict]:
    rows = await conn.fetch(
        """
        INSERT INTO Purchase (purchase_date, id_business)
        VALUES ($1, $2) RETURNING *
        """, purchase.purchase_date, id_business
    )
    return dict(rows[0])

async def delete_purchase(conn: asyncpg.Connection, id_business: int, id_purchase: int) -> Optional[dict]:
    rows = await conn.fetch(
        """
        DELETE FROM Purchase WHERE id_business = $1 AND id_purchase = $2 RETURNING *
        """, id_business, id_purchase
    )
    return dict(rows[0]) if rows else None

async def create_purchase_with_items(conn: asyncpg.Connection, id_business: int, purchase_data: PurchaseWithItemsCreate) -> dict:
    async with conn.transaction():
        purchase_row = await conn.fetchrow(
            """
            INSERT INTO Purchase (purchase_date, id_business)
            VALUES ($1, $2) RETURNING *
            """, purchase_data.purchase_date, id_business
        )
        id_purchase = purchase_row['id_purchase']

        for item in purchase_data.items:
            material_exists = await conn.fetchval(
                "SELECT 1 FROM Material WHERE id_material = $1 AND id_business = $2",
                item.id_material, id_business
            )
            if not material_exists:
                raise ValueError(f"El material {item.id_material} no pertenece a tu negocio o no existe.")
            await conn.execute(
                """
                INSERT INTO Product (id_material, expiration_date, quantity, entry_date)
                VALUES ($1, $2, $3, $4)
                """, item.id_material, item.expiration_date, item.quantity, item.entry_date
            )

            if item.id_supplier:
                await conn.execute(
                    """
                    INSERT INTO PurchaseItem (id_purchase, id_material, quantity_purchased, unit_price_purchased, id_supplier)
                    VALUES ($1, $2, $3, $4, $5)
                    """, id_purchase, item.id_material, item.quantity, item.unit_price, item.id_supplier
                )
            else:
                await conn.execute(
                    """
                    INSERT INTO PurchaseItem (id_purchase, id_material, quantity_purchased, unit_price_purchased)
                    VALUES ($1, $2, $3, $4)
                    """, id_purchase, item.id_material, item.quantity, item.unit_price
                )

        return dict(purchase_row)