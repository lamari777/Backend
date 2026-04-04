from fastapi import APIRouter, Depends, HTTPException, status
import asyncpg

from app.api.dependencies import get_db, get_current_business
from app.schemas.supplier_schema import SupplierCreate, SupplierUpdate, SupplierOut
from app.repositories import supplier_repo

router = APIRouter(prefix="/supplier", tags=["Supplier"])

@router.get("/", response_model=list[SupplierOut], summary="Listado de todos los proveedores de un negocio")
async def listar_proveedores(
    conn: asyncpg.Connection = Depends(get_db),
    current_payload: dict = Depends(get_current_business)
):
    id_business = int(current_payload["sub"])
    return await supplier_repo.get_suppliers_by_business(conn, id_business)

@router.get("/{id_supplier}", response_model=SupplierOut, summary="Obtener un proveedor por ID")
async def obtener_proveedor(
    id_supplier: int, 
    conn: asyncpg.Connection = Depends(get_db),
    current_payload: dict = Depends(get_current_business)
):
    id_business = int(current_payload["sub"])
    supplier = await supplier_repo.get_supplier_by_id(conn, id_supplier, id_business)
    if not supplier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proveedor no encontrado o no pertenece a tu negocio")
    return supplier

@router.post("/", response_model=SupplierOut, status_code=status.HTTP_201_CREATED, summary="Crear un nuevo proveedor")
async def crear_proveedor(
    supplier: SupplierCreate, 
    conn: asyncpg.Connection = Depends(get_db),
    current_payload: dict = Depends(get_current_business)
):
    id_business = int(current_payload["sub"])
    try:
        return await supplier_repo.create_supplier(conn, supplier, id_business)
    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya existe un proveedor con ese nombre en tu negocio")

@router.patch("/{id_supplier}", response_model=SupplierOut, summary="Actualizar un proveedor")
async def actualizar_proveedor(
    id_supplier: int, 
    supplier: SupplierUpdate, 
    conn: asyncpg.Connection = Depends(get_db),
    current_payload: dict = Depends(get_current_business)
):
    id_business = int(current_payload["sub"])
    try:
        updated = await supplier_repo.update_supplier(conn, id_supplier, supplier, id_business)
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proveedor no encontrado o no pertenece a tu negocio")
        return updated
    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya existe un proveedor con ese nombre en tu negocio")

@router.delete("/{id_supplier}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar un proveedor")
async def eliminar_proveedor(
    id_supplier: int, 
    conn: asyncpg.Connection = Depends(get_db),
    current_payload: dict = Depends(get_current_business)
):
    id_business = int(current_payload["sub"])
    deleted = await supplier_repo.delete_supplier(conn, id_supplier, id_business)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proveedor no encontrado o no pertenece a tu negocio")