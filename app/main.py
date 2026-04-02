from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.db.database import connect_db, disconnect_db
from app.api.endpoints import inventario, business


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestiona el ciclo de vida de la aplicación: conecta la BD al arrancar y la cierra al parar."""
    await connect_db()
    yield
    await disconnect_db()


app = FastAPI(
    title="API de Gestión de Inventario",
    description="Backend para gestionar el inventario. Desarrollado con FastAPI y PostgreSQL (Neon.tech).",
    version="0.1.0",
    lifespan=lifespan,
)


# Health check: útil para monitorizar que la app está viva (Koyeb también lo usará)
@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "ok", "message": "API de inventario funcionando correctamente."}


# Registrar routers
app.include_router(inventario.router, prefix="/api/v1")
app.include_router(business.router, prefix="/api/v1")
