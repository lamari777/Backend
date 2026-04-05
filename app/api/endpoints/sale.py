from fastapi import APIRouter, Depends, HTTPException, status
import asyncpg
from typing import Optional

from app.api.dependencies import get_db, get_current_business
from app.schemas.sale_schema import SaleCreate, SaleOut
from app.repositories import sale_repo

router = APIRouter(prefix="/sale", tags=["Sale"])

@router.get("/", response_model=list[SaleOut], summary="Listado de todas las ventas de un negocio")
async def listar_ventas(
    conn: asyncpg.Connection = Depends(get_db),
    current_payload: dict = Depends(get_current_business)
):
    id_business = int(current_payload["sub"])
    return await sale_repo.get_sales_by_business(conn, id_business)

@router.get("/{id_sale}", response_model=SaleOut, summary="Obtener una venta por ID")
async def obtener_venta(
    id_sale: int, 
    conn: asyncpg.Connection = Depends(get_db),
    current_payload: dict = Depends(get_current_business)
):
    id_business = int(current_payload["sub"])
    sale = await sale_repo.get_sale_by_id(conn, id_business, id_sale)
    if not sale:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venta no encontrada o no pertenece a tu negocio")
    return sale

@router.post("/", response_model=SaleOut, status_code=status.HTTP_201_CREATED, summary="Crear una nueva venta")
async def crear_venta(
    sale: SaleCreate, 
    conn: asyncpg.Connection = Depends(get_db),
    current_payload: dict = Depends(get_current_business)
):
    id_business = int(current_payload["sub"])
    try:
        return await sale_repo.create_sale(conn, id_business, sale)
    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya existe una venta con ese ID en tu negocio")

@router.delete("/{id_sale}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar una venta")
async def eliminar_venta(
    id_sale: int, 
    conn: asyncpg.Connection = Depends(get_db),
    current_payload: dict = Depends(get_current_business)
):
    id_business = int(current_payload["sub"])
    deleted = await sale_repo.delete_sale(conn, id_business, id_sale)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venta no encontrada o no pertenece a tu negocio")