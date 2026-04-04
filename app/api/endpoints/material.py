from fastapi import APIRouter, Depends, HTTPException, status
import asyncpg
from typing import Optional

from app.api.dependencies import get_db, get_current_business
from app.schemas.material_schema import MaterialCreate, MaterialUpdate, MaterialOut
from app.repositories import material_repo

router = APIRouter(prefix="/material", tags=["Material"])

@router.get("/", response_model=list[MaterialOut], summary="Listado de todos los materiales de un negocio")
async def listar_materiales(
    conn: asyncpg.Connection = Depends(get_db),
    current_payload: dict = Depends(get_current_business)
):
    id_business = int(current_payload["sub"])
    return await material_repo.get_materials_by_business(conn, id_business)

@router.get("/{id_material}", response_model=MaterialOut, summary="Obtener un material por ID")
async def obtener_material(
    id_material: int, 
    conn: asyncpg.Connection = Depends(get_db),
    current_payload: dict = Depends(get_current_business)
):
    id_business = int(current_payload["sub"])
    material = await material_repo.get_material_by_id(conn, id_business, id_material)
    if not material:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material no encontrado o no pertenece a tu negocio")
    return material

@router.post("/", response_model=MaterialOut, status_code=status.HTTP_201_CREATED, summary="Crear un nuevo material")
async def crear_material(
    material: MaterialCreate, 
    conn: asyncpg.Connection = Depends(get_db),
    current_payload: dict = Depends(get_current_business)
):
    id_business = int(current_payload["sub"])
    try:
        return await material_repo.create_material(conn, id_business, material)
    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya existe un material con ese nombre en tu negocio")

@router.patch("/{id_material}", response_model=MaterialOut, summary="Actualizar un material")
async def actualizar_material(
    id_material: int, 
    material: MaterialUpdate, 
    conn: asyncpg.Connection = Depends(get_db),
    current_payload: dict = Depends(get_current_business)
):
    id_business = int(current_payload["sub"])
    try:
        updated = await material_repo.update_material(conn, id_business, id_material, material)
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material no encontrado o no pertenece a tu negocio")
        return updated
    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya existe un material con ese nombre en tu negocio")

@router.delete("/{id_material}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar un material")
async def eliminar_material(
    id_material: int, 
    conn: asyncpg.Connection = Depends(get_db),
    current_payload: dict = Depends(get_current_business)
):
    id_business = int(current_payload["sub"])
    deleted = await material_repo.delete_material(conn, id_business, id_material)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material no encontrado o no pertenece a tu negocio")
