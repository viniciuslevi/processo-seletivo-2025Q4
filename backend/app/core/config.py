"""
Configurações da aplicação
"""
import os
from typing import Optional


class Settings:
    """Configurações centralizadas da aplicação"""
    
    # API
    API_V1_PREFIX: str = "/integrations"
    PROJECT_NAME: str = "EyesOnAsset API"
    
    # JWT
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", 
        "your-secret-key-here-change-in-production-make-it-very-secure"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1  # 1 minuto conforme requisito
    
    # Credenciais fixas (Nível 4)
    FIXED_LOGIN: str = "eyesonasset"
    FIXED_PASSWORD: str = "eyesonasset"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./assets.db")


settings = Settings()
