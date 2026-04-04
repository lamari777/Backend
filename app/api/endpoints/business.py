from fastapi import APIRouter, Depends, HTTPException, status
import asyncpg

from app.api.dependencies import get_db, get_current_business
from app.schemas.business_schema import BusinessUpdate, BusinessOut
from app.repositories import business_repo

router = APIRouter(prefix="/business", tags=["Business"])

@router.get("/", response_model=list[BusinessOut], summary="Listar todos los negocios")
async def listar_businesses(
    conn: asyncpg.Connection = Depends(get_db),
    current_payload: dict = Depends(get_current_business)
):
    return await business_repo.get_all_businesses(conn)


@router.patch("/me", response_model=BusinessOut, summary="Actualizar datos de tu negocio")
async def actualizar_business(
    business: BusinessUpdate, 
    conn: asyncpg.Connection = Depends(get_db),
    current_payload: dict = Depends(get_current_business)
):
    """Actualiza la información del negocio actualmente autenticado."""
    id_business = int(current_payload["sub"])
    try:
        updated = await business_repo.update_business(conn, id_business, business)
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El negocio no existe")
        return updated
    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ese email ya está en uso por otro negocio")


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar tu negocio")
async def eliminar_business(
    conn: asyncpg.Connection = Depends(get_db),
    current_payload: dict = Depends(get_current_business)
):
    """Elimina la cuenta del negocio actualmente logueado."""
    id_business = int(current_payload["sub"])
    deleted = await business_repo.delete_business(conn, id_business)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El negocio no pudo ser eliminado o ya no existe")
