from fastapi import APIRouter, Depends, HTTPException, status
import asyncpg
from typing import Optional

from app.api.dependencies import get_db, get_current_business
from app.schemas.product_schema import ProductCreate, ProductUpdate, ProductOut
from app.repositories import product_repo

router = APIRouter(prefix="/product", tags=["Product"])

@router.get("/", response_model=list[ProductOut], summary="Listado de todos los productos de un negocio")
async def listar_productos(
    conn: asyncpg.Connection = Depends(get_db),
    current_payload: dict = Depends(get_current_business)
):
    id_business = int(current_payload["sub"])
    return await product_repo.get_products_by_business(conn, id_business)

@router.get("/{id_product}", response_model=ProductOut, summary="Obtener un producto por ID")
async def obtener_producto(
    id_product: int, 
    conn: asyncpg.Connection = Depends(get_db),
    current_payload: dict = Depends(get_current_business)
):
    id_business = int(current_payload["sub"])
    product = await product_repo.get_product_by_id(conn, id_business, id_product)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado o no pertenece a tu negocio")
    return product

@router.post("/", response_model=ProductOut, status_code=status.HTTP_201_CREATED, summary="Crear un nuevo producto")
async def crear_producto(
    product: ProductCreate, 
    conn: asyncpg.Connection = Depends(get_db),
    current_payload: dict = Depends(get_current_business)
):
    id_business = int(current_payload["sub"])
    try:
        return await product_repo.create_product(conn, id_business, product)
    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya existe un producto con ese nombre en tu negocio")

@router.patch("/{id_product}", response_model=ProductOut, summary="Actualizar un producto")
async def actualizar_producto(
    id_product: int, 
    product: ProductUpdate, 
    conn: asyncpg.Connection = Depends(get_db),
    current_payload: dict = Depends(get_current_business)
):
    id_business = int(current_payload["sub"])
    try:
        updated = await product_repo.update_product(conn, id_business, id_product, product)
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado o no pertenece a tu negocio")
        return updated
    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya existe un producto con ese nombre en tu negocio")

@router.delete("/{id_product}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar un producto")
async def eliminar_producto(
    id_product: int, 
    conn: asyncpg.Connection = Depends(get_db),
    current_payload: dict = Depends(get_current_business)
):
    id_business = int(current_payload["sub"])
    deleted = await product_repo.delete_product(conn, id_business, id_product)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado o no pertenece a tu negocio")