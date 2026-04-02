import asyncpg
from app.core.config import DATABASE_URL

# Pool de conexiones global. Se crea al arrancar la aplicación.
_pool: asyncpg.Pool | None = None


async def connect_db():
    """Inicializa el pool de conexiones a Neon.tech. Llamar al arrancar la app."""
    global _pool
    _pool = await asyncpg.create_pool(dsn=DATABASE_URL, min_size=1, max_size=10)
    print("Conexión al pool de base de datos establecida.")


async def disconnect_db():
    """Cierra el pool de conexiones. Llamar al apagar la app."""
    global _pool
    if _pool:
        await _pool.close()
        print("Pool de base de datos cerrado.")


def get_pool() -> asyncpg.Pool:
    """Devuelve el pool de conexiones activo."""
    if _pool is None:
        raise RuntimeError("El pool de base de datos no está inicializado. ¿Se llamó a connect_db()?")
    return _pool
