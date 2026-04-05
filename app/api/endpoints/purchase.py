from fastapi import APIRouter, Depends, HTTPException, status
import asyncpg
from typing import Optional

from app.api.dependencies import get_db, get_current_business
from app.schemas.purchase_schema import PurchaseCreate, PurchaseOut
from app.repositories import purchase_repo

router = APIRouter(prefix="/purchase", tags=["Purchase"])

@router.get("/", response_model=list[PurchaseOut], summary="Listado de todas las compras de un negocio")
async def listar_compras(
    conn: asyncpg.Connection = Depends(get_db),
    current_payload: dict = Depends(get_current_business)
):
    id_business = int(current_payload["sub"])
    return await purchase_repo.get_purchases_by_business(conn, id_business)

@router.get("/{id_purchase}", response_model=PurchaseOut, summary="Obtener una compra por ID")
async def obtener_compra(
    id_purchase: int, 
    conn: asyncpg.Connection = Depends(get_db),
    current_payload: dict = Depends(get_current_business)
):
    id_business = int(current_payload["sub"])
    purchase = await purchase_repo.get_purchase_by_id(conn, id_business, id_purchase)
    if not purchase:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compra no encontrada o no pertenece a tu negocio")
    return purchase

@router.post("/", response_model=PurchaseOut, status_code=status.HTTP_201_CREATED, summary="Crear una nueva compra")
async def crear_compra(
    purchase: PurchaseCreate, 
    conn: asyncpg.Connection = Depends(get_db),
    current_payload: dict = Depends(get_current_business)
):
    id_business = int(current_payload["sub"])
    try:
        return await purchase_repo.create_purchase(conn, id_business, purchase)
    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya existe una compra con ese ID en tu negocio")

@router.delete("/{id_purchase}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar una compra")
async def eliminar_compra(
    id_purchase: int, 
    conn: asyncpg.Connection = Depends(get_db),
    current_payload: dict = Depends(get_current_business)
):
    id_business = int(current_payload["sub"])
    deleted = await purchase_repo.delete_purchase(conn, id_business, id_purchase)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compra no encontrada o no pertenece a tu negocio")