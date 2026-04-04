from fastapi import APIRouter, Depends, HTTPException, status
import asyncpg

from app.api.dependencies import get_db, get_current_business
from app.schemas.category_schema import CategoryCreate, CategoryUpdate, CategoryOut
from app.repositories import category_repo

router = APIRouter(prefix="/category", tags=["Category"])

@router.get("/", response_model=list[CategoryOut], summary="Listar las categorías de tu negocio")
async def listar_categorias(
    conn: asyncpg.Connection = Depends(get_db),
    current_payload: dict = Depends(get_current_business)
):
    id_business = int(current_payload["sub"])
    return await category_repo.get_categories_by_business(conn, id_business)


@router.get("/{id_category}", response_model=CategoryOut, summary="Obtener una de tus categorías por ID")
async def obtener_categoria(
    id_category: int, 
    conn: asyncpg.Connection = Depends(get_db),
    current_payload: dict = Depends(get_current_business)
):
    id_business = int(current_payload["sub"])
    category = await category_repo.get_category_by_id(conn, id_category, id_business)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada o no pertenece a tu negocio")
    return category


@router.post("/", response_model=CategoryOut, status_code=status.HTTP_201_CREATED, summary="Crear una nueva categoría")
async def crear_categoria(
    category: CategoryCreate, 
    conn: asyncpg.Connection = Depends(get_db),
    current_payload: dict = Depends(get_current_business)
):
    id_business = int(current_payload["sub"])
    try:
        return await category_repo.create_category(conn, category, id_business)
    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya existe una categoría con ese nombre en tu negocio")


@router.patch("/{id_category}", response_model=CategoryOut, summary="Actualizar una de tus categorías")
async def actualizar_categoria(
    id_category: int, 
    category: CategoryUpdate, 
    conn: asyncpg.Connection = Depends(get_db),
    current_payload: dict = Depends(get_current_business)
):
    id_business = int(current_payload["sub"])
    try:
        updated = await category_repo.update_category(conn, id_category, category, id_business)
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada o no pertenece a tu negocio")
        return updated
    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya existe una categoría con ese nombre en tu negocio")


@router.delete("/{id_category}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar una de tus categorías")
async def eliminar_categoria(
    id_category: int, 
    conn: asyncpg.Connection = Depends(get_db),
    current_payload: dict = Depends(get_current_business)
):
    id_business = int(current_payload["sub"])
    deleted = await category_repo.delete_category(conn, id_category, id_business)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada o no pertenece a tu negocio")
