from fastapi import APIRouter, Depends, HTTPException, status
import asyncpg
from typing import Optional

from app.api.dependencies import get_db, get_current_business
from app.schemas.purchase_item_schema import PurchaseItemCreate, PurchaseItemOut
from app.repositories import purchase_item_repo

router = APIRouter(prefix="/purchase_item", tags=["Purchase Item"])

@router.get("/", response_model=list[PurchaseItemOut], summary="Listado de todos los items de una compra")
async def listar_items_compra(
    id_purchase: int,
    conn: asyncpg.Connection = Depends(get_db),
    current_payload: dict = Depends(get_current_business)
):
    id_business = int(current_payload["sub"])
    return await purchase_item_repo.get_purchase_items_by_purchase(conn, id_purchase)

@router.get("/{id_purchase_item}", response_model=PurchaseItemOut, summary="Obtener un item de una compra por ID")
async def obtener_item_compra(
    id_purchase: int,
    id_purchase_item: int,
    conn: asyncpg.Connection = Depends(get_db),
    current_payload: dict = Depends(get_current_business)
):
    id_business = int(current_payload["sub"])
    item = await purchase_item_repo.get_purchase_item_by_id(conn, id_purchase, id_purchase_item)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item de compra no encontrado o no pertenece a tu negocio")
    return item

@router.post("/", response_model=PurchaseItemOut, status_code=status.HTTP_201_CREATED, summary="Crear un nuevo item de compra")
async def crear_item_compra(
    id_purchase: int,
    item: PurchaseItemCreate,
    conn: asyncpg.Connection = Depends(get_db),
    current_payload: dict = Depends(get_current_business)
):
    id_business = int(current_payload["sub"])
    try:
        return await purchase_item_repo.create_purchase_item(conn, id_purchase, item)
    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya existe un item de compra con ese ID en tu negocio")

@router.delete("/{id_purchase_item}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar un item de compra")
async def eliminar_item_compra(
    id_purchase: int,
    id_purchase_item: int,
    conn: asyncpg.Connection = Depends(get_db),
    current_payload: dict = Depends(get_current_business)
):
    id_business = int(current_payload["sub"])
    deleted = await purchase_item_repo.delete_purchase_item(conn, id_purchase, id_purchase_item)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item de compra no encontrado o no pertenece a tu negocio")
