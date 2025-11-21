from contextlib import asynccontextmanager
import logging
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import api_router
from app.db.base import engine, Base
from app.db.models import Asset, Owner  # Importar modelos para criar tabelas

# Adicionar o diretório backend ao path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    logging.info("Starting up...")
    
    try:
        # Criar todas as tabelas no banco de dados
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        logger.info("Application started successfully")

    except Exception as e:
        logger.error(f"Error during startup: {e}")

    yield
    # Shutdown actions
    logging.info("Shutting down...")

app = FastAPI(
    title="EyesOnAsset API",
    description="API for managing physical assets and their owners",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://165.22.131.75:3000",
        "http://165.22.131.75",  # Adicionar sem porta também
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas da API v1
app.include_router(api_router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to the EyesOnAsset API",
        "version": "1.0.0",
        "docs": "/docs"
    }