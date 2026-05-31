import asyncpg
import json
from typing import Optional
from app.schemas.whatsapp_request_schema import WhatsAppRequestCreate

async def create_whatsapp_request(conn: asyncpg.Connection, id_business: int, request_data: WhatsAppRequestCreate) -> dict:
    json_str = request_data.json_summary
    if not isinstance(json_str, str):
        json_str = json.dumps(json_str)

    row = await conn.fetchrow(
        """
        INSERT INTO whatsapp_request (
            id_business, 
            request_phone_number, 
            message_id, 
            json_summary, 
            status, 
            rejection_reason, 
            created_at
        ) VALUES ($1, $2, $3, $4, $5, $6, NOW())
        RETURNING *
        """,
        id_business,
        request_data.request_phone_number,
        request_data.message_id,
        json_str,
        request_data.status,
        request_data.rejection_reason
    )
    return dict(row)

async def get_whatsapp_requests_by_business(conn: asyncpg.Connection, id_business: int) -> list[dict]:
    rows = await conn.fetch(
        """
        SELECT * FROM whatsapp_request 
        WHERE id_business = $1 
        ORDER BY created_at DESC
        """,
        id_business
    )
    return [dict(row) for row in rows]

async def update_whatsapp_request_status(
    conn: asyncpg.Connection,
    id_business: int,
    id_request: int,
    status: str,
    rejection_reason: Optional[str] = None
) -> Optional[dict]:
    row = await conn.fetchrow(
        """
        UPDATE whatsapp_request
        SET status = $1, rejection_reason = $2
        WHERE id_request = $3 AND id_business = $4
        RETURNING *
        """,
        status,
        rejection_reason,
        id_request,
        id_business
    )
    return dict(row) if row else None
