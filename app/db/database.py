import asyncpg
from app.core.config import DATABASE_URL

_pool: asyncpg.Pool | None = None


async def connect_db():
    global _pool
    _pool = await asyncpg.create_pool(dsn=DATABASE_URL, min_size=1, max_size=10)
    print("Conexión al pool de base de datos establecida.")


async def disconnect_db():
    global _pool
    if _pool:
        await _pool.close()
        print("Pool de base de datos cerrado.")


def get_pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("El pool de base de datos no está inicializado. ¿Se llamó a connect_db()?")
    return _pool
