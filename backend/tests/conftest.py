"""
Configuração e fixtures compartilhadas para todos os testes
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base
from app.db.sessions import get_db


# Criar engine de teste em memória
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Habilitar foreign keys no SQLite para os testes
from sqlalchemy import event
from sqlalchemy.engine import Engine

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Habilita foreign keys no SQLite em cada conexão"""
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


@pytest.fixture(scope="function")
def db_session():
    """
    Cria uma nova sessão de banco de dados para cada teste.
    Garante que os testes são isolados.
    """
    # Criar todas as tabelas
    Base.metadata.create_all(bind=engine)
    
    # Criar sessão
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        # Limpar todas as tabelas após o teste
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    Cria um cliente de teste do FastAPI com banco de dados em memória.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_owner_data():
    """Dados de exemplo para criar um owner"""
    return {
        "name": "João da Silva",
        "email": "joao.silva@empresa.com",
        "phone": "+55 11 98765-4321"
    }


@pytest.fixture
def sample_asset_data():
    """Dados de exemplo para criar um asset (sem owner_id)"""
    return {
        "name": "Aeronave Boeing 737",
        "category": "Aeronave"
    }


@pytest.fixture
def auth_headers(client):
    """Retorna headers com token JWT válido"""
    response = client.post(
        "/integrations/auth",
        data={
            "login": "eyesonasset",
            "password": "eyesonasset"
        }
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def created_owner(client, sample_owner_data, auth_headers):
    """Cria um owner no banco de dados de teste e retorna seus dados"""
    response = client.post(
        "/integrations/owner",
        json=sample_owner_data,
        headers=auth_headers
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def created_asset(client, created_owner, sample_asset_data, auth_headers):
    """Cria um asset no banco de dados de teste e retorna seus dados"""
    asset_data = {**sample_asset_data, "owner": created_owner["id"]}
    response = client.post(
        "/integrations/asset",
        json=asset_data,
        headers=auth_headers
    )
    assert response.status_code == 201
    return response.json()
