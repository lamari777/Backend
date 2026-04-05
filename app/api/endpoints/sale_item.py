from fastapi import APIRouter, Depends, HTTPException, status
import asyncpg
from typing import Optional

from app.api.dependencies import get_db, get_current_business
from app.schemas.sale_item_schema import SaleItemCreate, SaleItemOut
from app.repositories import sale_item_repo

router = APIRouter(prefix="/sale_item", tags=["Sale Item"])

@router.get("/", response_model=list[SaleItemOut], summary="Listado de todos los items de una venta")
async def listar_items_venta(
    id_sale: int,
    conn: asyncpg.Connection = Depends(get_db),
    current_payload: dict = Depends(get_current_business)
):
    id_business = int(current_payload["sub"])
    return await sale_item_repo.get_sale_items_by_sale(conn, id_sale)

@router.get("/{id_sale_item}", response_model=SaleItemOut, summary="Obtener un item de una venta por ID")
async def obtener_item_venta(
    id_sale: int,
    id_sale_item: int,
    conn: asyncpg.Connection = Depends(get_db),
    current_payload: dict = Depends(get_current_business)
):
    id_business = int(current_payload["sub"])
    item = await sale_item_repo.get_sale_item_by_id(conn, id_sale, id_sale_item)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item de venta no encontrado o no pertenece a tu negocio")
    return item

@router.post("/", response_model=SaleItemOut, status_code=status.HTTP_201_CREATED, summary="Crear un nuevo item de venta")
async def crear_item_venta(
    id_sale: int,
    item: SaleItemCreate,
    conn: asyncpg.Connection = Depends(get_db),
    current_payload: dict = Depends(get_current_business)
):
    id_business = int(current_payload["sub"])
    try:
        return await sale_item_repo.create_sale_item(conn, id_sale, item)
    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya existe un item de venta con ese ID en tu negocio")

@router.delete("/{id_sale_item}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar un item de venta")
async def eliminar_item_venta(
    id_sale: int,
    id_sale_item: int,
    conn: asyncpg.Connection = Depends(get_db),
    current_payload: dict = Depends(get_current_business)
):
    id_business = int(current_payload["sub"])
    deleted = await sale_item_repo.delete_sale_item(conn, id_sale, id_sale_item)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item de venta no encontrado o no pertenece a tu negocio")
