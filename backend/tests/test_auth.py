"""
Testes para autenticação JWT
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from jose import jwt
from app.core.config import settings


def test_login_success(client):
    """Testa login com credenciais corretas"""
    response = client.post(
        "/integrations/auth",
        data={
            "login": "eyesonasset",
            "password": "eyesonasset"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verificar estrutura da resposta
    assert "access_token" in data
    assert "token_type" in data
    assert "expires_in" in data
    
    # Verificar valores
    assert data["token_type"] == "bearer"
    assert data["expires_in"] == 60
    assert isinstance(data["access_token"], str)
    assert len(data["access_token"]) > 0


def test_login_invalid_credentials(client):
    """Testa login com credenciais inválidas"""
    response = client.post(
        "/integrations/auth",
        data={
            "login": "wrong",
            "password": "wrong"
        }
    )
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciais inválidas"


def test_login_missing_login(client):
    """Testa login sem o campo login"""
    response = client.post(
        "/integrations/auth",
        data={
            "password": "eyesonasset"
        }
    )
    
    assert response.status_code == 422  # Validation error


def test_login_missing_password(client):
    """Testa login sem o campo password"""
    response = client.post(
        "/integrations/auth",
        data={
            "login": "eyesonasset"
        }
    )
    
    assert response.status_code == 422  # Validation error


def test_token_structure(client):
    """Verifica a estrutura do token JWT gerado"""
    response = client.post(
        "/integrations/auth",
        data={
            "login": "eyesonasset",
            "password": "eyesonasset"
        }
    )
    
    token = response.json()["access_token"]
    
    # Decodificar o token (sem verificar a assinatura para este teste)
    payload = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM]
    )
    
    # Verificar campos obrigatórios
    assert "sub" in payload
    assert "exp" in payload
    assert payload["sub"] == "eyesonasset"


def test_protected_route_without_token(client):
    """Testa acesso a rota protegida sem token"""
    response = client.get("/integrations/owners")
    
    assert response.status_code == 403
    assert "Not authenticated" in response.json()["detail"]


def test_protected_route_with_invalid_token(client):
    """Testa acesso a rota protegida com token inválido"""
    response = client.get(
        "/integrations/owners",
        headers={"Authorization": "Bearer token-invalido"}
    )
    
    assert response.status_code == 401
    assert "Token inválido" in response.json()["detail"]


def test_protected_route_with_valid_token(client, created_owner):
    """Testa acesso a rota protegida com token válido"""
    # Obter token
    auth_response = client.post(
        "/integrations/auth",
        data={
            "login": "eyesonasset",
            "password": "eyesonasset"
        }
    )
    token = auth_response.json()["access_token"]
    
    # Acessar rota protegida
    response = client.get(
        "/integrations/owners",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_protected_route_missing_bearer_prefix(client):
    """Testa token sem o prefixo 'Bearer'"""
    # Obter token
    auth_response = client.post(
        "/integrations/auth",
        data={
            "login": "eyesonasset",
            "password": "eyesonasset"
        }
    )
    token = auth_response.json()["access_token"]
    
    # Tentar acessar sem o prefixo Bearer
    response = client.get(
        "/integrations/owners",
        headers={"Authorization": token}  # Sem "Bearer "
    )
    
    # Deve falhar
    assert response.status_code in [401, 403]


def test_expired_token(client):
    """Testa token expirado"""
    # Criar um token já expirado
    expired_time = datetime.utcnow() - timedelta(minutes=5)
    payload = {
        "sub": "eyesonasset",
        "exp": expired_time
    }
    expired_token = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    # Tentar usar o token expirado
    response = client.get(
        "/integrations/owners",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    
    assert response.status_code == 401
    assert "expirado" in response.json()["detail"].lower()


def test_create_owner_with_auth(client):
    """Testa criação de owner com autenticação"""
    # Obter token
    auth_response = client.post(
        "/integrations/auth",
        data={
            "login": "eyesonasset",
            "password": "eyesonasset"
        }
    )
    token = auth_response.json()["access_token"]
    
    # Criar owner
    owner_data = {
        "name": "Test Owner Auth",
        "email": f"auth_{datetime.now().timestamp()}@test.com",
        "phone": "11987654321"
    }
    
    response = client.post(
        "/integrations/owner",
        json=owner_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 201
    assert response.json()["name"] == owner_data["name"]


def test_create_owner_without_auth(client):
    """Testa criação de owner sem autenticação"""
    owner_data = {
        "name": "Test Owner",
        "email": "test@test.com",
        "phone": "11987654321"
    }
    
    response = client.post(
        "/integrations/owner",
        json=owner_data
    )
    
    assert response.status_code == 403


def test_get_owner_with_auth(client, created_owner):
    """Testa busca de owner com autenticação"""
    # Obter token
    auth_response = client.post(
        "/integrations/auth",
        data={
            "login": "eyesonasset",
            "password": "eyesonasset"
        }
    )
    token = auth_response.json()["access_token"]
    
    # Buscar owner
    response = client.get(
        f"/integrations/owner/{created_owner['id']}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["id"] == created_owner["id"]


def test_update_owner_with_auth(client, created_owner):
    """Testa atualização de owner com autenticação"""
    # Obter token
    auth_response = client.post(
        "/integrations/auth",
        data={
            "login": "eyesonasset",
            "password": "eyesonasset"
        }
    )
    token = auth_response.json()["access_token"]
    
    # Atualizar owner
    response = client.put(
        f"/integrations/owner/{created_owner['id']}",
        json={"name": "Updated Name"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"


def test_delete_owner_with_auth(client, created_owner):
    """Testa deleção de owner com autenticação"""
    # Obter token
    auth_response = client.post(
        "/integrations/auth",
        data={
            "login": "eyesonasset",
            "password": "eyesonasset"
        }
    )
    token = auth_response.json()["access_token"]
    
    # Deletar owner
    response = client.delete(
        f"/integrations/owner/{created_owner['id']}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 204


def test_create_asset_with_auth(client, created_owner):
    """Testa criação de asset com autenticação"""
    # Obter token
    auth_response = client.post(
        "/integrations/auth",
        data={
            "login": "eyesonasset",
            "password": "eyesonasset"
        }
    )
    token = auth_response.json()["access_token"]
    
    # Criar asset
    asset_data = {
        "name": "Test Asset Auth",
        "category": "Test Category",
        "owner": created_owner["id"]
    }
    
    response = client.post(
        "/integrations/asset",
        json=asset_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 201
    assert response.json()["name"] == asset_data["name"]


def test_token_reuse(client):
    """Testa reutilização do mesmo token em múltiplas requisições"""
    # Obter token
    auth_response = client.post(
        "/integrations/auth",
        data={
            "login": "eyesonasset",
            "password": "eyesonasset"
        }
    )
    token = auth_response.json()["access_token"]
    
    # Usar o token várias vezes
    for _ in range(3):
        response = client.get(
            "/integrations/owners",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200


def test_malformed_authorization_header(client):
    """Testa header de autorização malformado"""
    # Sem espaço entre Bearer e token
    response = client.get(
        "/integrations/owners",
        headers={"Authorization": "Bearertoken123"}
    )
    assert response.status_code in [401, 403]
    
    # Palavra-chave errada
    response = client.get(
        "/integrations/owners",
        headers={"Authorization": "Basic token123"}
    )
    assert response.status_code in [401, 403]
    
    # Apenas Bearer sem token
    response = client.get(
        "/integrations/owners",
        headers={"Authorization": "Bearer "}
    )
    assert response.status_code in [401, 403]
