from fastapi import APIRouter, Depends, HTTPException, status
import asyncpg

from app.api.dependencies import get_db, get_current_business
from app.schemas.auth_schema import LoginRequest, TokenResponse
from app.schemas.business_schema import BusinessCreate, BusinessOut
from app.repositories import business_repo
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=BusinessOut, status_code=status.HTTP_201_CREATED,
             summary="Registrar un nuevo negocio (público)")
async def register(business: BusinessCreate, conn: asyncpg.Connection = Depends(get_db)):
    """Crea un nuevo negocio. Es el único endpoint accesible sin autenticación (junto a /auth/login)."""
    try:
        return await business_repo.create_business(conn, business)
    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )


@router.post("/login", response_model=TokenResponse, summary="Iniciar sesión (público)")
async def login(data: LoginRequest, conn: asyncpg.Connection = Depends(get_db)):
    """Autentica al negocio con email o nombre + contraseña y devuelve un JWT Bearer."""
    business = await business_repo.authenticate_business(conn, data.identifier, data.password)
    if not business:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(data={"sub": str(business["id_business"])})
    return TokenResponse(access_token=token)


@router.get("/me", response_model=BusinessOut, summary="Obtener datos del negocio logueado")
async def get_me(
    current_payload: dict = Depends(get_current_business),
    conn: asyncpg.Connection = Depends(get_db)
):
    """Devuelve los datos reales del negocio autenticado mediante el JWT proporcionado en el header."""
    id_business = int(current_payload["sub"])
    business = await business_repo.get_business_by_id(conn, id_business)
    
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="El negocio asociado a este token ya no existe."
        )
        
    return business
