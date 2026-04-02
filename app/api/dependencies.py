import asyncpg
from app.db.database import get_pool


async def get_db() -> asyncpg.Connection:
    """
    Dependencia de FastAPI para inyectar una conexión del pool en cada endpoint.
    Uso en un endpoint:
        async def mi_endpoint(conn: asyncpg.Connection = Depends(get_db)):
    """
    async with get_pool().acquire() as connection:
        yield connection
