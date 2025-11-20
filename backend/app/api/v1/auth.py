"""
Rotas de autenticação
"""
from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Form

from app.schemas.auth import LoginRequest, TokenResponse
from app.core.config import settings
from app.core.security import create_access_token


router = APIRouter(prefix="/integrations", tags=["Authentication"])


@router.post("/auth", response_model=TokenResponse, status_code=200)
def login(login: str = Form(...), password: str = Form(...)):
    """
    Autenticação com login e senha fixos.
    
    Credenciais válidas:
    - login: eyesonasset
    - password: eyesonasset
    
    Retorna um token JWT válido por 1 minuto.
    """
    # Validar credenciais fixas
    if login != settings.FIXED_LOGIN or password != settings.FIXED_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Criar token JWT
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": login},
        expires_delta=access_token_expires
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Converter para segundos
    )
