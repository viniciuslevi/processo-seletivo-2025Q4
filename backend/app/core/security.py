"""
Utilitários de segurança e autenticação JWT
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings


# Security scheme para Swagger
security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Cria um token JWT com os dados fornecidos.
    
    Args:
        data: Dicionário com os dados a serem incluídos no token
        expires_delta: Tempo de expiração do token (opcional)
    
    Returns:
        Token JWT codificado
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt


def verify_token(token: str) -> dict:
    """
    Verifica e decodifica um token JWT.
    
    Args:
        token: Token JWT a ser verificado
    
    Returns:
        Payload decodificado do token
    
    Raises:
        HTTPException: Se o token for inválido ou expirado
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Dependency para validar o token JWT em rotas protegidas.
    
    Args:
        credentials: Credenciais HTTP Bearer do header Authorization
    
    Returns:
        Payload do token (dados do usuário)
    
    Raises:
        HTTPException: Se o token for inválido ou expirado
    """
    token = credentials.credentials
    payload = verify_token(token)
    
    # Validar que o token tem o campo 'sub' (subject)
    if payload.get("sub") is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload
