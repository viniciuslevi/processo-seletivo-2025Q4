"""
Schemas para autenticação JWT
"""
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Schema para requisição de login"""
    login: str = Field(..., min_length=1, max_length=100, description="Login do usuário")
    password: str = Field(..., min_length=1, max_length=100, description="Senha do usuário")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "login": "eyesonasset",
                    "password": "eyesonasset"
                }
            ]
        }
    }


class TokenResponse(BaseModel):
    """Schema para resposta com token JWT"""
    access_token: str = Field(..., description="Token JWT de acesso")
    token_type: str = Field(default="bearer", description="Tipo do token")
    expires_in: int = Field(..., description="Tempo de expiração em segundos")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                    "expires_in": 60
                }
            ]
        }
    }
