from fastapi import APIRouter, Depends, HTTPException, status
import asyncpg

from app.api.dependencies import get_db
from app.schemas.business_schema import BusinessUpdate, BusinessOut
from app.repositories import business_repo

router = APIRouter(prefix="/business", tags=["Business"])

@router.get("/", response_model=list[BusinessOut], summary="Listar todos los negocios")
async def listar_businesses(conn: asyncpg.Connection = Depends(get_db)):
    return await business_repo.get_all_businesses(conn)

@router.get("/{id_business}", response_model=BusinessOut, summary="Obtener un negocio por ID")
async def obtener_business(id_business: int, conn: asyncpg.Connection = Depends(get_db)):
    business = await business_repo.get_business_by_id(conn, id_business)
    if not business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Negocio no encontrado")
    return business


@router.patch("/{id_business}", response_model=BusinessOut, summary="Actualizar datos de un negocio")
async def actualizar_business(id_business: int, business: BusinessUpdate, conn: asyncpg.Connection = Depends(get_db)):
    try:
        updated = await business_repo.update_business(conn, id_business, business)
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Negocio no encontrado")
        return updated
    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El email ya está en uso")

@router.delete("/{id_business}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar un negocio")
async def eliminar_business(id_business: int, conn: asyncpg.Connection = Depends(get_db)):
    deleted = await business_repo.delete_business(conn, id_business)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Negocio no encontrado")
