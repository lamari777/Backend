import asyncpg
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.db.database import get_pool
from app.core.security import decode_access_token

_bearer = HTTPBearer()


async def get_db() -> asyncpg.Connection:
    """
    Dependencia de FastAPI para inyectar una conexión del pool en cada endpoint.
    Uso en un endpoint:
        async def mi_endpoint(conn: asyncpg.Connection = Depends(get_db)):
    """
    async with get_pool().acquire() as connection:
        yield connection


async def get_current_business(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> dict:
    """Valida el JWT Bearer y devuelve el payload del token.
    Lanza 401 si el token es inválido o ha expirado.
    """
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload
